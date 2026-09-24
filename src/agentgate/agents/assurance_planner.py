from agentgate.schemas import (
	AssurancePlan,
	ChangeAssessment,
	ReleasePolicy,
	RiskTaxonomy,
	TestCatalogue,
	TestResultBundle,
)
from agentgate.tools.policy_tools import RISK_TO_TESTS


class AssurancePlanner:
	"""Deterministic adapter that maps confirmed risks to governed evidence."""

	execution_mode = "local_deterministic"

	def plan(
		self,
		assessment: ChangeAssessment,
		policy: ReleasePolicy,
		taxonomy: RiskTaxonomy,
		catalogue: TestCatalogue,
		result_bundle: TestResultBundle | None = None,
	) -> AssurancePlan:
		risk_ids = {category.risk_id for category in taxonomy.categories}
		confirmed = set(assessment.confirmed_risk_categories)
		unknown_risks = confirmed - risk_ids
		if unknown_risks:
			raise ValueError(f"unknown confirmed risk categories: {sorted(unknown_risks)}")
		test_ids = {test.test_id for test in catalogue.tests}
		required_tests = sorted(
		{
			test_id
			for risk_id in confirmed
			for test_id in RISK_TO_TESTS.get(risk_id, ())
		}
		& test_ids
	)
		triggered_controls: set[str] = set()
		for control in policy.controls:
			if control.control_id in {
				"missing-evidence-blocker",
				"evidence-reference-integrity",
			}:
				continue
			if not set(control.trigger_categories) & confirmed:
				continue
			if control.control_id == "authority-requires-approval":
				if any(
					(
						(
							change.path.endswith("/action_type")
							or change.path.endswith("/access_mode")
						)
						and change.after in {"WRITE", "EXECUTE"}
					)
					for change in assessment.changes
				):
					triggered_controls.add(control.control_id)
			elif control.control_id == "brokerage-escalation-testing":
				if any(
					change.path.startswith("/permissions/")
					and change.path.endswith("/access_mode")
					and change.after == "WRITE"
					for change in assessment.changes
				):
					triggered_controls.add(control.control_id)
			else:
				triggered_controls.add(control.control_id)
		control_ids = sorted(triggered_controls)
		if control_ids and "evidence-reference-integrity" in test_ids:
			required_tests = sorted(set(required_tests) | {"evidence-reference-integrity"})
		statuses = (
			{} if result_bundle is None else {result.test_id: result.status.value for result in result_bundle.results}
		)
		missing = sorted(
			test_id for test_id in required_tests if statuses.get(test_id) != "PASS"
		)
		if missing and "missing-evidence-blocker" in {
			control.control_id for control in policy.controls
		}:
			control_ids = sorted(set(control_ids) | {"missing-evidence-blocker"})
		human_review_required = bool(
			confirmed & {"financial_action", "human_approval", "external_side_effect", "autonomy_change"}
		)
		if missing:
			human_review_required = True
		evidence_refs = [f"control:{control_id}" for control_id in control_ids]
		evidence_refs.extend(f"test:{test_id}" for test_id in required_tests)
		return AssurancePlan(
			schema_version="1.0",
			execution_mode=self.execution_mode,
			candidate_release_id=assessment.candidate_release_id,
			confirmed_risk_categories=sorted(confirmed),
			control_ids=control_ids,
			required_test_ids=required_tests,
			missing_evidence_test_ids=missing,
			human_review_required=human_review_required,
			rationale=(
				"Evidence is mapped from confirmed risks to the fixed policy and test catalogue."
			),
			evidence_refs=evidence_refs,
		)
