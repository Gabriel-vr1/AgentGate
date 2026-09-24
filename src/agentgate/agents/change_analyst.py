from agentgate.schemas import ChangeAssessment, ChangeAssessmentItem, ManifestDiff


class ChangeAnalyst:
	"""Deterministic adapter that explains an exact manifest diff."""

	execution_mode = "local_deterministic"

	@staticmethod
	def _area(path: str) -> str:
		root = path.split("/")[1] if path.startswith("/") else ""
		if root == "tools":
			return "capability"
		if root == "permissions":
			return "permission"
		if root == "capabilities":
			return "capability"
		if root == "autonomy_level":
			return "autonomy"
		if root == "approval":
			return "approval"
		if root == "model":
			return "model"
		if root == "system_prompt_sha256":
			return "prompt"
		return "metadata"

	def analyze(self, diff: ManifestDiff) -> ChangeAssessment:
		changes = [
			ChangeAssessmentItem(
				path=change.path,
				change_type=change.change_type,
				area=self._area(change.path),
				before=change.before,
				after=change.after,
				explanation=(
					f"{self._area(change.path).replace('_', ' ')} changed at "
					f"{change.path}."
				),
				evidence_refs=[change.path],
			)
			for change in diff.changes
		]
		if changes:
			summary = f"{len(changes)} exact manifest change(s) identified."
		else:
			summary = "No manifest changes identified."
		return ChangeAssessment(
			schema_version="1.0",
			execution_mode=self.execution_mode,
			baseline_release_id=diff.baseline_release_id,
			candidate_release_id=diff.candidate_release_id,
			changes=changes,
			confirmed_risk_categories=diff.confirmed_risk_categories,
			summary=summary,
		)
