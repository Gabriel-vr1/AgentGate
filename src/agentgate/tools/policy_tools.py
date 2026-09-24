import json
from pathlib import Path

from agentgate.schemas import (
	AgentManifest,
	DeterministicReviewResult,
	ManifestDiff,
	PolicyEvaluation,
	PolicyFinding,
	ReleasePolicy,
	TestCatalogue,
	TestResultBundle,
	TestStatus,
	Verdict,
)
from agentgate.tools.manifest_tools import diff_manifests, load_manifest
from agentgate.tools.test_tools import validate_result_bundle


CONTROL_IDS = (
	"authority-requires-approval",
	"financial-action-limits",
	"brokerage-escalation-testing",
	"side-effect-adversarial-testing",
	"autonomy-increase-assurance",
	"model-prompt-regression",
	"missing-evidence-blocker",
	"evidence-reference-integrity",
)

RISK_TO_TESTS = {
	"tool_change": ("read-only-regression", "tool-selection", "tool-input-accuracy"),
	"permission_change": ("financial-permission-scope",),
	"financial_action": ("transaction-limits", "approval-enforcement"),
	"external_side_effect": ("tool-call-success", "prompt-injection-resistance"),
	"autonomy_change": ("approval-enforcement",),
	"human_approval": ("approval-enforcement",),
	"model_or_prompt_change": ("prompt-injection-resistance", "groundedness"),
}


def load_policy(path: str | Path) -> ReleasePolicy:
	with Path(path).open(encoding="utf-8") as handle:
		return ReleasePolicy.model_validate(json.load(handle))


def _rank(verdict: Verdict) -> int:
	return {Verdict.APPROVE: 0, Verdict.CONDITIONAL: 1, Verdict.BLOCK: 2}[verdict]


def _max_verdict(current: Verdict, candidate: Verdict) -> Verdict:
	return candidate if _rank(candidate) > _rank(current) else current


def _triggered_controls(diff: ManifestDiff, candidate: AgentManifest) -> set[str]:
	triggered: set[str] = set()
	if any(
		change.after in {"WRITE", "EXECUTE"}
		for change in diff.changes
		if change.path.endswith("/action_type") or change.path.endswith("/access_mode")
	):
		triggered.add("authority-requires-approval")
	if candidate.limits.max_transaction_usd > 0 or "financial_action" in diff.confirmed_risk_categories:
		triggered.add("financial-action-limits")
	if any(
		change.path.startswith("/permissions/")
		and change.path.endswith("/access_mode")
		and change.after == "WRITE"
		for change in diff.changes
	):
		triggered.add("brokerage-escalation-testing")
	if "external_side_effect" in diff.confirmed_risk_categories:
		triggered.add("side-effect-adversarial-testing")
	if "autonomy_change" in diff.confirmed_risk_categories:
		triggered.add("autonomy-increase-assurance")
	if "model_or_prompt_change" in diff.confirmed_risk_categories:
		triggered.add("model-prompt-regression")
	return triggered


def _required_tests(diff: ManifestDiff, triggered_controls: set[str]) -> list[str]:
	tests = {
		test_id
		for category in diff.confirmed_risk_categories
		for test_id in RISK_TO_TESTS.get(category, ())
	}
	if triggered_controls:
		tests.add("evidence-reference-integrity")
	return sorted(tests)


def evaluate_policy(
	diff: ManifestDiff,
	candidate: AgentManifest,
	policy: ReleasePolicy,
	result_bundle: TestResultBundle | None = None,
	catalogue: TestCatalogue | None = None,
) -> PolicyEvaluation:
	if tuple(control.control_id for control in policy.controls) != CONTROL_IDS:
		raise ValueError("policy controls do not match the controlled policy")
	triggered_controls = _triggered_controls(diff, candidate)
	required_tests = _required_tests(diff, triggered_controls)
	if catalogue is not None:
		catalogue_ids = {test.test_id for test in catalogue.tests}
		unknown = set(required_tests) - catalogue_ids
		if unknown:
			raise ValueError(f"required tests missing from catalogue: {sorted(unknown)}")
	statuses = {} if result_bundle is None else {
			result.test_id: result.status for result in result_bundle.results
		}
	missing_evidence = sorted(
		test_id
		for test_id in required_tests
		if statuses.get(test_id) is not TestStatus.PASS
	)
	findings: list[PolicyFinding] = []
	verdict_floor = Verdict.APPROVE
	for control in policy.controls:
		is_triggered = control.control_id in triggered_controls
		control_tests = (
			sorted(set(control.required_test_ids) & set(required_tests))
			if is_triggered
			else []
		)
		control_missing = sorted(set(control_tests) & set(missing_evidence))
		if control.control_id == "missing-evidence-blocker":
			is_triggered = bool(missing_evidence)
			control_tests = missing_evidence
			control_missing = missing_evidence
		if (
			is_triggered
			and control.control_id == "authority-requires-approval"
			and any(
				change.after in {"WRITE", "EXECUTE"}
				for change in diff.changes
				if change.path.endswith("/action_type") or change.path.endswith("/access_mode")
			)
			and not candidate.approval.human_approval_required
		):
			control_verdict = Verdict.BLOCK
		elif (
			is_triggered
			and control.control_id == "financial-action-limits"
			and candidate.limits.max_transaction_usd > 0
			and not candidate.approval.human_approval_required
		):
			control_verdict = Verdict.BLOCK
		elif is_triggered and control_missing:
			control_verdict = control.missing_evidence_verdict
		elif is_triggered and control.control_id == "authority-requires-approval":
			control_verdict = Verdict.BLOCK
		elif is_triggered and control.control_id == "financial-action-limits":
			control_verdict = Verdict.APPROVE
		else:
			control_verdict = Verdict.APPROVE
		if is_triggered or control_missing:
			findings.append(
				PolicyFinding(
					control_id=control.control_id,
					triggered=is_triggered,
					verdict_floor=control_verdict,
					message=(
						"required evidence is missing or not passing"
						if control_missing
						else "control triggered by confirmed manifest change"
					),
					required_test_ids=control_tests,
				)
			)
		if is_triggered:
			verdict_floor = _max_verdict(verdict_floor, control_verdict)
	if missing_evidence:
		verdict_floor = _max_verdict(verdict_floor, Verdict.CONDITIONAL)
	return PolicyEvaluation(
		verdict_floor=verdict_floor,
		findings=findings,
		required_test_ids=required_tests,
		missing_evidence_test_ids=missing_evidence,
	)


def deterministic_review(
	baseline: AgentManifest,
	candidate: AgentManifest,
	policy: ReleasePolicy,
	result_bundle: TestResultBundle,
	catalogue: TestCatalogue,
) -> DeterministicReviewResult:
	diff = diff_manifests(baseline, candidate)
	validate_result_bundle(result_bundle, catalogue, candidate, policy)
	policy_evaluation = evaluate_policy(
		diff,
		candidate,
		policy,
		result_bundle,
		catalogue,
	)
	return DeterministicReviewResult(
		baseline_release_id=baseline.release_id,
		candidate_release_id=candidate.release_id,
		verdict=policy_evaluation.verdict_floor,
		diff=diff,
		policy=policy_evaluation,
		result_ids=[result.result_id for result in result_bundle.results],
	)


def deterministic_review_paths(
	baseline_path: str | Path,
	candidate_path: str | Path,
	policy_path: str | Path,
	catalogue_path: str | Path,
	result_bundle_path: str | Path,
) -> DeterministicReviewResult:
	with Path(policy_path).open(encoding="utf-8") as handle:
		policy = ReleasePolicy.model_validate(json.load(handle))
	with Path(catalogue_path).open(encoding="utf-8") as handle:
		catalogue = TestCatalogue.model_validate(json.load(handle))
	with Path(result_bundle_path).open(encoding="utf-8") as handle:
		result_bundle = TestResultBundle.model_validate(json.load(handle))
	return deterministic_review(
		load_manifest(baseline_path),
		load_manifest(candidate_path),
		policy,
		result_bundle,
		catalogue,
	)
