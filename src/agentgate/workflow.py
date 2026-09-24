from pathlib import Path

from agentgate.agents.assurance_planner import AssurancePlanner
from agentgate.agents.change_analyst import ChangeAnalyst
from agentgate.agents.release_judge import ReleaseJudge
from agentgate.schemas import (
	AgentManifest,
	AssurancePlan,
	ChangeAssessment,
	DeterministicReviewResult,
	ReleaseDecision,
	ReleasePolicy,
	RiskTaxonomy,
	TestCatalogue,
	TestResultBundle,
	WorkflowFailure,
)
from agentgate.tools.manifest_tools import diff_manifests, load_manifest
from agentgate.tools.policy_tools import deterministic_review
from agentgate.tools.test_tools import (
	EvidenceReferenceError,
	load_catalogue,
	validate_evidence_references,
	validate_result_bundle,
)


class WorkflowError(ValueError):
	def __init__(self, failure: WorkflowFailure):
		self.failure = failure
		super().__init__(failure.message)


def _fail(stage: str, error: Exception) -> WorkflowError:
	return WorkflowError(
		WorkflowFailure(status="FAILED", stage=stage, message=str(error))
	)


def _validate_assessment(assessment: ChangeAssessment, diff) -> None:
	expected = [
		(change.path, change.change_type, change.before, change.after)
		for change in diff.changes
	]
	actual = [
		(change.path, change.change_type, change.before, change.after)
		for change in assessment.changes
	]
	if actual != expected:
		raise ValueError("change assessment does not match the exact manifest diff")
	if assessment.confirmed_risk_categories != diff.confirmed_risk_categories:
		raise ValueError("change assessment risk categories do not match the manifest diff")
	if (
		assessment.baseline_release_id != diff.baseline_release_id
		or assessment.candidate_release_id != diff.candidate_release_id
	):
		raise ValueError("change assessment release IDs do not match the manifest diff")


def _validate_change_references(
	assessment: ChangeAssessment,
	baseline: AgentManifest,
	candidate: AgentManifest,
	policy: ReleasePolicy,
	catalogue: TestCatalogue,
) -> None:
	for change in assessment.changes:
		for reference in change.evidence_refs:
			try:
				validate_evidence_references([reference], candidate, policy, catalogue)
			except EvidenceReferenceError:
				validate_evidence_references([reference], baseline, policy, catalogue)


def _validate_plan(plan: AssurancePlan, review: DeterministicReviewResult) -> None:
	expected_tests = review.policy.required_test_ids
	if plan.required_test_ids != expected_tests:
		raise ValueError("assurance plan tests do not match deterministic test selection")
	if plan.missing_evidence_test_ids != review.policy.missing_evidence_test_ids:
		raise ValueError("assurance plan evidence status does not match deterministic results")
	expected_controls = {finding.control_id for finding in review.policy.findings}
	if set(plan.control_ids) != expected_controls:
		raise ValueError("assurance plan controls do not match deterministic policy findings")


def _validate_decision(
	decision: ReleaseDecision,
	review: DeterministicReviewResult,
	manifest: AgentManifest,
	policy: ReleasePolicy,
	catalogue: TestCatalogue,
) -> ReleaseDecision:
	if decision.verdict_floor is not review.policy.verdict_floor:
		raise ValueError("release decision changed the deterministic verdict floor")
	ranks = {"APPROVE": 0, "CONDITIONAL": 1, "BLOCK": 2}
	if ranks[decision.verdict.value] < ranks[decision.verdict_floor.value]:
		raise ValueError("release decision downgraded the deterministic verdict floor")
	if (
		decision.baseline_release_id != review.baseline_release_id
		or decision.candidate_release_id != review.candidate_release_id
	):
		raise ValueError("release decision release IDs do not match the review")
	all_references = list(decision.evidence_refs)
	for finding in [*decision.blockers, *decision.conditions]:
		all_references.extend(finding.evidence_refs)
	validate_evidence_references(all_references, manifest, policy, catalogue)
	return decision


def run_workflow(
	baseline_path: str | Path,
	candidate_path: str | Path,
	policy_path: str | Path,
	taxonomy_path: str | Path,
	catalogue_path: str | Path,
	result_bundle_path: str | Path,
	change_analyst: ChangeAnalyst | None = None,
	assurance_planner: AssurancePlanner | None = None,
	release_judge: ReleaseJudge | None = None,
) -> ReleaseDecision:
	try:
		baseline = load_manifest(baseline_path)
		candidate = load_manifest(candidate_path)
		policy = ReleasePolicy.model_validate_json(Path(policy_path).read_text())
		taxonomy = RiskTaxonomy.model_validate_json(Path(taxonomy_path).read_text())
		catalogue = load_catalogue(catalogue_path)
		result_bundle = TestResultBundle.model_validate_json(
			Path(result_bundle_path).read_text()
		)
		validate_result_bundle(result_bundle, catalogue, candidate, policy)
		diff = diff_manifests(baseline, candidate)
	except (OSError, ValueError, TypeError) as error:
		raise _fail("input_validation", error) from error

	try:
		assessment = (change_analyst or ChangeAnalyst()).analyze(diff)
		assessment = ChangeAssessment.model_validate(assessment.model_dump())
		_validate_assessment(assessment, diff)
		_validate_change_references(assessment, baseline, candidate, policy, catalogue)
	except (EvidenceReferenceError, ValueError, TypeError) as error:
		raise _fail("change_analyst", error) from error

	try:
		planner = assurance_planner or AssurancePlanner()
		plan = planner.plan(assessment, policy, taxonomy, catalogue, result_bundle)
		plan = AssurancePlan.model_validate(plan.model_dump())
		validate_evidence_references(plan.evidence_refs, candidate, policy, catalogue)
	except (EvidenceReferenceError, ValueError, TypeError) as error:
		raise _fail("assurance_planner", error) from error

	try:
		review = deterministic_review(
			baseline, candidate, policy, result_bundle, catalogue
		)
		_validate_plan(plan, review)
	except (EvidenceReferenceError, ValueError, TypeError) as error:
		raise _fail("deterministic_policy", error) from error

	try:
		decision = (release_judge or ReleaseJudge()).judge(
			assessment, plan, review, result_bundle
		)
		decision = ReleaseDecision.model_validate(decision.model_dump())
		return _validate_decision(decision, review, candidate, policy, catalogue)
	except (EvidenceReferenceError, ValueError, TypeError) as error:
		raise _fail("release_judge", error) from error