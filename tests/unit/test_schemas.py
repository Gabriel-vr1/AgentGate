from decimal import Decimal

import pytest
from pydantic import ValidationError

from agentgate.schemas import (
    ActionType,
    AgentManifest,
    EvaluationCase,
    ReleasePolicy,
    RiskTaxonomy,
    TestCatalogue as CatalogueSchema,
    ToolSpec,
    Verdict,
)


def valid_manifest_data() -> dict:
    return {
        "schema_version": "1.0",
        "agent_id": "trading-agent",
        "release_id": "release-1",
        "display_name": "Synthetic Trading Agent",
        "version": "1.0.0",
        "description": "A synthetic agent for assurance demonstrations.",
        "model": {
            "provider": "test-provider",
            "deployment_name": "test-deployment",
            "temperature": 0.2,
        },
        "system_prompt_sha256": "a" * 64,
        "tools": [
            {
                "tool_id": "market-read",
                "name": "Market Read",
                "description": "Reads synthetic market data.",
                "action_type": "READ",
                "side_effects": False,
                "requires_confirmation": False,
            }
        ],
        "permissions": [
            {
                "permission_id": "market-data",
                "resource": "synthetic-market",
                "access_mode": "READ",
                "scopes": ["prices"],
            }
        ],
        "capabilities": [
            {
                "capability_id": "market-analysis",
                "description": "Analyzes synthetic market data.",
                "action_type": "ADVISORY",
                "enabled": True,
            }
        ],
        "autonomy_level": "ASSISTED",
        "approval": {
            "human_approval_required": True,
            "enforced_by": "WORKFLOW",
            "required_for_actions": ["execute-trade"],
        },
        "limits": {
            "currency": "USD",
            "max_transaction_usd": "100.00",
            "max_actions_per_run": 5,
        },
    }


def test_valid_agent_manifest():
    manifest = AgentManifest.model_validate(valid_manifest_data())

    assert manifest.agent_id == "trading-agent"
    assert manifest.limits.max_transaction_usd == Decimal("100.00")


@pytest.mark.parametrize(
    "mutation",
    [
        lambda data: data.pop("agent_id"),
        lambda data: data.update(unexpected="value"),
        lambda data: data.update(system_prompt_sha256="A" * 64),
    ],
)
def test_invalid_manifest_data_rejected(mutation):
    data = valid_manifest_data()
    mutation(data)

    with pytest.raises(ValidationError):
        AgentManifest.model_validate(data)


@pytest.mark.parametrize("field", ["tools", "permissions", "capabilities"])
def test_duplicate_manifest_ids_rejected(field):
    data = valid_manifest_data()
    item = data[field][0].copy()
    data[field].append(item)

    with pytest.raises(ValidationError):
        AgentManifest.model_validate(data)


def test_invalid_approval_combination_rejected():
    data = valid_manifest_data()
    data["approval"] = {
        "human_approval_required": True,
        "enforced_by": "NONE",
        "required_for_actions": [],
    }

    with pytest.raises(ValidationError):
        AgentManifest.model_validate(data)


def test_negative_transaction_limit_rejected():
    data = valid_manifest_data()
    data["limits"]["max_transaction_usd"] = -1

    with pytest.raises(ValidationError):
        AgentManifest.model_validate(data)


def valid_policy_control(control_id: str = "approval-control") -> dict:
    return {
        "control_id": control_id,
        "title": "Approval required",
        "description": "Requires review for execution.",
        "severity": "HIGH",
        "non_overridable": True,
        "trigger_categories": ["financial-risk"],
        "required_test_ids": ["approval-test"],
        "missing_evidence_verdict": "BLOCK",
    }


def test_duplicate_policy_control_id_rejected():
    data = {
        "schema_version": "1.0",
        "policy_id": "release-policy",
        "version": "1.0",
        "description": "Release controls.",
        "controls": [valid_policy_control(), valid_policy_control()],
    }

    with pytest.raises(ValidationError):
        ReleasePolicy.model_validate(data)


def test_duplicate_risk_id_rejected():
    category = {
        "risk_id": "financial-risk",
        "title": "Financial risk",
        "description": "Potential financial harm.",
        "default_severity": "HIGH",
    }
    data = {
        "schema_version": "1.0",
        "taxonomy_id": "risk-taxonomy",
        "version": "1.0",
        "categories": [category, category.copy()],
    }

    with pytest.raises(ValidationError):
        RiskTaxonomy.model_validate(data)


def test_duplicate_test_id_rejected():
    test_case = {
        "test_id": "approval-test",
        "title": "Approval test",
        "description": "Checks approval evidence.",
        "risk_ids": ["financial-risk"],
        "deterministic": True,
        "required_evidence": ["approval-log"],
    }
    data = {
        "schema_version": "1.0",
        "catalogue_id": "test-catalogue",
        "version": "1.0",
        "tests": [test_case, test_case.copy()],
    }

    with pytest.raises(ValidationError):
        CatalogueSchema.model_validate(data)


def test_valid_evaluation_case():
    case = EvaluationCase(
        case_id="baseline-case",
        title="Baseline release case",
        baseline_manifest_path="data/manifests/baseline.json",
        candidate_manifest_path="data/manifests/candidate.json",
        expected_verdict=Verdict.CONDITIONAL,
        expected_control_ids=["approval-control"],
        expected_required_test_ids=["approval-test"],
    )

    assert case.expected_verdict is Verdict.CONDITIONAL


def test_enum_values_serialize_exactly_as_declared():
    assert [verdict.value for verdict in Verdict] == [
        "APPROVE",
        "CONDITIONAL",
        "BLOCK",
    ]
    assert ToolSpec(
        tool_id="read-tool",
        name="Read",
        description="Reads data.",
        action_type=ActionType.READ,
        side_effects=False,
        requires_confirmation=False,
    ).model_dump()["action_type"] == "READ"


def test_manifest_json_round_trip_preserves_manifest():
    manifest = AgentManifest.model_validate(valid_manifest_data())

    assert AgentManifest.model_validate_json(manifest.model_dump_json()) == manifest
