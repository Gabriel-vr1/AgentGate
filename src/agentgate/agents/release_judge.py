from agentgate.schemas import (
	AssurancePlan,
	DecisionFinding,
	DeterministicReviewResult,
	ReleaseDecision,
	TestResultBundle,
	Verdict,
)


class ReleaseJudge:
	"""Deterministic adapter that renders policy evidence without lowering its floor."""

	execution_mode = "local_deterministic"

	@staticmethod
	def _references(control_id: str, test_ids: list[str]) -> list[str]:
		return [f"control:{control_id}", *(f"test:{test_id}" for test_id in test_ids)]

	def judge(
		self,
		assessment,
		plan: AssurancePlan,
		review: DeterministicReviewResult,
		result_bundle: TestResultBundle,
	) -> ReleaseDecision:
		blockers: list[DecisionFinding] = []
		conditions: list[DecisionFinding] = []
		remediation: list[str] = []
		all_refs: list[str] = []
		all_refs.extend(plan.evidence_refs)
		for finding in review.policy.findings:
			references = self._references(finding.control_id, finding.required_test_ids)
			all_refs.extend(references)
			if finding.verdict_floor is Verdict.BLOCK:
				blockers.append(
					DecisionFinding(
						code=finding.control_id,
						message=finding.message,
						evidence_refs=references,
					)
				)
				remediation.append(f"Resolve control {finding.control_id} before release.")
			elif finding.verdict_floor is Verdict.CONDITIONAL:
				conditions.append(
					DecisionFinding(
						code=finding.control_id,
						message=finding.message,
						evidence_refs=references,
					)
				)
				remediation.append(f"Complete evidence for control {finding.control_id}.")
		floor = review.policy.verdict_floor
		verdict = floor
		if verdict is Verdict.BLOCK and not blockers:
			blockers.append(
				DecisionFinding(
					code="deterministic-block",
					message="The deterministic policy floor blocks this release.",
					evidence_refs=[f"test:{test_id}" for test_id in plan.required_test_ids],
				)
			)
		return ReleaseDecision(
			schema_version="1.0",
			execution_mode=self.execution_mode,
			baseline_release_id=review.baseline_release_id,
			candidate_release_id=review.candidate_release_id,
			verdict=verdict,
			verdict_floor=floor,
			blockers=blockers,
			conditions=conditions,
			evidence_refs=sorted(set(all_refs)),
			remediation=remediation,
		)
