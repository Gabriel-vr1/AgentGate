import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from agentgate.agents.assurance_planner import AssurancePlanner
from agentgate.agents.change_analyst import ChangeAnalyst
from agentgate.agents.release_judge import ReleaseJudge
from agentgate.schemas import (
	AssurancePlan,
	ChangeAssessment,
	ReleaseDecision,
	RiskTaxonomy,
	TestResultBundle as ResultBundleSchema,
	Verdict,
)
from agentgate.tools.manifest_tools import diff_manifests, load_manifest
from agentgate.tools.policy_tools import deterministic_review, load_policy
from agentgate.tools.test_tools import load_catalogue, validate_evidence_references
from agentgate.workflow import WorkflowError, run_workflow


ROOT = Path(__file__).parents[2]
BASELINE = ROOT / "data/manifests/baseline_agent.json"
POLICY = ROOT / "data/policies/release_policy.json"
TAXONOMY = ROOT / "data/policies/risk_taxonomy.json"
CATALOGUE = ROOT / "data/test_catalogue.json"


def workflow_paths(candidate: str, result: str | None = None) -> tuple[Path, ...]:
	return (
		BASELINE,
		ROOT / f"data/manifests/{candidate}.json",
		POLICY,
		TAXONOMY,
		CATALOGUE,
		ROOT / f"data/test_results/{result or candidate}.json",
	)


def test_three_agent_handoffs_are_schema_valid_and_grounded():
	baseline = load_manifest(BASELINE)
	candidate = load_manifest(ROOT / "data/manifests/unsafe_candidate.json")
	policy = load_policy(POLICY)
	taxonomy = RiskTaxonomy.model_validate_json(TAXONOMY.read_text())
	catalogue = load_catalogue(CATALOGUE)
	bundle = ResultBundleSchema.model_validate_json(
		(ROOT / "data/test_results/unsafe_candidate.json").read_text()
	)
	diff = diff_manifests(baseline, candidate)
	assessment = ChangeAnalyst().analyze(diff)
	plan = AssurancePlanner().plan(assessment, policy, taxonomy, catalogue, bundle)
	review = deterministic_review(baseline, candidate, policy, bundle, catalogue)
	decision = ReleaseJudge().judge(assessment, plan, review, bundle)

	assert ChangeAssessment.model_validate(assessment.model_dump()).execution_mode == "local_deterministic"
	assert AssurancePlan.model_validate(plan.model_dump()).required_test_ids == review.policy.required_test_ids
	assert decision.execution_mode == "local_deterministic"
	assert decision.verdict is Verdict.BLOCK
	validate_evidence_references(
		plan.evidence_refs + decision.evidence_refs,
		candidate,
		policy,
		catalogue,
	)


def test_unsafe_safe_and_incomplete_workflow_verdicts():
	assert run_workflow(*workflow_paths("unsafe_candidate")).verdict is Verdict.BLOCK
	assert run_workflow(*workflow_paths("safe_candidate")).verdict is Verdict.APPROVE
	assert run_workflow(*workflow_paths("incomplete_candidate")).verdict is Verdict.CONDITIONAL


def test_malformed_change_handoff_fails_safely():
	class BadAnalyst(ChangeAnalyst):
		def analyze(self, diff):
			assessment = super().analyze(diff)
			return assessment.model_copy(update={"confirmed_risk_categories": ["invented-risk"]})

	with pytest.raises(WorkflowError) as error:
		run_workflow(*workflow_paths("safe_candidate"), change_analyst=BadAnalyst())
	assert error.value.failure.stage == "change_analyst"


def test_malformed_evidence_handoff_fails_safely():
	class BadJudge(ReleaseJudge):
		def judge(self, assessment, plan, review, result_bundle):
			decision = super().judge(assessment, plan, review, result_bundle)
			return decision.model_copy(update={"evidence_refs": ["test:not-real"]})

	with pytest.raises(WorkflowError) as error:
		run_workflow(*workflow_paths("safe_candidate"), release_judge=BadJudge())
	assert error.value.failure.stage == "release_judge"


def test_missing_evidence_is_not_a_pass():
	decision = run_workflow(*workflow_paths("incomplete_candidate"))
	assert decision.verdict is Verdict.CONDITIONAL
	assert decision.verdict is not Verdict.APPROVE


def test_release_decision_rejects_floor_downgrade():
	with pytest.raises(ValidationError):
		ReleaseDecision(
			schema_version="1.0",
			execution_mode="local_deterministic",
			baseline_release_id="baseline-1",
			candidate_release_id="candidate-1",
			verdict=Verdict.APPROVE,
			verdict_floor=Verdict.BLOCK,
			blockers=[],
			conditions=[],
			evidence_refs=[],
			remediation=[],
		)


def test_all_evaluation_cases_match_expected_verdicts():
	results = []
	for line in (ROOT / "evaluation/eval_cases.jsonl").read_text().splitlines():
		case = json.loads(line)
		result = run_workflow(
			ROOT / case["baseline_manifest_path"],
			ROOT / case["candidate_manifest_path"],
			POLICY,
			TAXONOMY,
			CATALOGUE,
			ROOT / case["result_bundle_path"],
		)
		results.append(result.verdict.value == case["expected_verdict"])
	assert len(results) == 10
	assert all(results)


def test_cli_smoke_execution():
	env = os.environ.copy()
	env["PYTHONPATH"] = str(ROOT / "src")
	completed = subprocess.run(
		[sys.executable, "app.py", "run", "unsafe"],
		cwd=ROOT,
		env=env,
		capture_output=True,
		text=True,
		check=False,
	)
	assert completed.returncode == 0
	assert "Final verdict: BLOCK" in completed.stdout
	assert "Execution mode: local_deterministic" in completed.stdout