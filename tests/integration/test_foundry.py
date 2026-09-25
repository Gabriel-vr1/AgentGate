import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from agentgate.agents.foundry import (
    FoundrySession, FoundryChangeAnalyst, FoundryAssurancePlanner, FoundryReleaseJudge,
    Recommendation, connect,
)
from agentgate.config import Settings
from agentgate.tracing import RunTrace
from agentgate.workflow import WorkflowError, run_workflow
from tests.integration.test_local_workflow import workflow_paths


def response(payload):
    return SimpleNamespace(id="resp_mock", usage=None, output_text=json.dumps(payload))


def session(outputs):
    client = Mock()
    client.responses.create.side_effect = outputs
    trace = RunTrace("foundry")
    return FoundrySession(client, "mock-deployment", trace)


def run(cloud, candidate="unsafe_candidate"):
    return run_workflow(*workflow_paths(candidate), change_analyst=FoundryChangeAnalyst(cloud),
                        assurance_planner=FoundryAssurancePlanner(cloud), release_judge=FoundryReleaseJudge(cloud))


@pytest.mark.parametrize("candidate,verdict", [("unsafe_candidate", "BLOCK"),
    ("safe_candidate", "APPROVE"), ("incomplete_candidate", "CONDITIONAL")])
def test_cloud_preserves_authoritative_decision(candidate, verdict):
    cloud = session([response({"explanation": "Supplied changes."}),
                     response({"explanation": "Controlled tests."}),
                     response({"explanation": "Evidence reviewed.", "verdict": verdict})])
    actual = run(cloud, candidate)
    expected = run_workflow(*workflow_paths(candidate)).model_dump()
    expected["execution_mode"] = "foundry"
    assert actual.model_dump() == expected
    assert cloud.client.responses.create.call_count == 3
    assert all(s["status"] == "validated" for s in cloud.trace.document["spans"])
    assert cloud.client.responses.create.call_args.kwargs["store"] is False


def test_one_repair_succeeds():
    cloud = session([response({"extra": "invalid"}), response({"explanation": "Repaired."})])
    assert cloud.ask("Change Analyst", {}).explanation == "Repaired."
    assert cloud.client.responses.create.call_count == 2


@pytest.mark.parametrize("payload", [
    {"explanation": "Downgrade", "verdict": "APPROVE"},
    {"explanation": "Invented", "verdict": "BLOCK", "evidence_refs": ["test:fake"]},
    {"explanation": "", "verdict": "BLOCK"},
])
def test_invalid_judge_output_is_rejected_after_one_repair(payload):
    cloud = session([response(payload), response(payload)])
    with pytest.raises(ValueError, match="one repair"):
        cloud.ask("Release Judge", {}, Recommendation, "BLOCK")
    assert cloud.client.responses.create.call_count == 2


def test_transport_failure_stops_without_retry_or_secret_leak():
    cloud = session([TimeoutError("secret-token-must-not-appear")])
    with pytest.raises(WorkflowError, match="unavailable") as error:
        run(cloud)
    assert error.value.failure.stage == "change_analyst"
    assert cloud.client.responses.create.call_count == 1
    assert "secret-token" not in json.dumps(cloud.trace.document)
    assert "secret-token" not in str(error.value)


def test_judge_downgrade_cannot_escape_workflow():
    cloud = session([response({"explanation": "Changes."}), response({"explanation": "Plan."}),
                     response({"explanation": "Unsafe approval", "verdict": "APPROVE"}),
                     response({"explanation": "Unsafe approval", "verdict": "APPROVE"})])
    with pytest.raises(WorkflowError) as error:
        run(cloud)
    assert error.value.failure.stage == "release_judge"


@pytest.mark.parametrize("endpoint", ["http://example.com", "https://evil.com/api/projects/x",
    "https://user:password@x.services.ai.azure.com/api/projects/x", ""])
def test_configuration_rejects_credential_exfiltration_endpoints(endpoint):
    settings = Settings(_env_file=None, AZURE_AI_PROJECT_ENDPOINT=endpoint,
                        AZURE_AI_MODEL_DEPLOYMENT_NAME="model")
    with pytest.raises(ValueError, match="endpoint"):
        with connect(settings, RunTrace("foundry")):
            pytest.fail("must not connect")


def test_python_findings_cannot_be_removed():
    from agentgate.agents.release_judge import ReleaseJudge
    class BadJudge(ReleaseJudge):
        def judge(self, *args):
            return super().judge(*args).model_copy(update={"blockers": [], "remediation": []})
    with pytest.raises(WorkflowError, match="Python-owned"):
        run_workflow(*workflow_paths("unsafe_candidate"), release_judge=BadJudge())
