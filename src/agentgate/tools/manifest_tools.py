import json
from pathlib import Path
from typing import Any

from agentgate.schemas import AgentManifest, ManifestChange, ManifestDiff


RISK_CATEGORIES = (
	"tool_change",
	"permission_change",
	"financial_action",
	"external_side_effect",
	"autonomy_change",
	"human_approval",
	"model_or_prompt_change",
)


def load_manifest(path: str | Path) -> AgentManifest:
	with Path(path).open(encoding="utf-8") as handle:
		return AgentManifest.model_validate(json.load(handle))


def _pointer(path: tuple[str, ...]) -> str:
	return "" if not path else "/" + "/".join(
		part.replace("~", "~0").replace("/", "~1") for part in path
	)


def _walk_changes(
	baseline: Any,
	candidate: Any,
	path: tuple[str, ...] = (),
) -> list[tuple[str, str, Any, Any]]:
	if isinstance(baseline, dict) and isinstance(candidate, dict):
		changes: list[tuple[str, str, Any, Any]] = []
		for key in sorted(set(baseline) | set(candidate)):
			child_path = path + (key,)
			if key not in baseline:
				changes.append((_pointer(child_path), "added", None, candidate[key]))
			elif key not in candidate:
				changes.append((_pointer(child_path), "removed", baseline[key], None))
			else:
				changes.extend(_walk_changes(baseline[key], candidate[key], child_path))
		return changes
	if isinstance(baseline, list) and isinstance(candidate, list):
		changes = []
		for index in range(max(len(baseline), len(candidate))):
			child_path = path + (str(index),)
			if index >= len(baseline):
				changes.append((_pointer(child_path), "added", None, candidate[index]))
			elif index >= len(candidate):
				changes.append((_pointer(child_path), "removed", baseline[index], None))
			else:
				changes.extend(_walk_changes(baseline[index], candidate[index], child_path))
		return changes
	if baseline != candidate:
		return [(_pointer(path), "modified", baseline, candidate)]
	return []


def _risk_categories(path: str, before: Any, after: Any) -> list[str]:
	parts = path.split("/")
	root = parts[1] if len(parts) > 1 else ""
	categories: set[str] = set()
	if root == "tools":
		categories.add("tool_change")
		tool_value = after if isinstance(after, dict) else before
		if isinstance(tool_value, dict) and tool_value.get("side_effects"):
			categories.add("external_side_effect")
		if isinstance(tool_value, dict) and tool_value.get("action_type") in {"WRITE", "EXECUTE"}:
			categories.add("external_side_effect")
		if path.endswith("/side_effects") and after is True:
			categories.add("external_side_effect")
		if path.endswith("/action_type") and after in {"WRITE", "EXECUTE"}:
			categories.add("external_side_effect")
	elif root == "permissions":
		categories.add("permission_change")
		if path.endswith("/access_mode") and after == "WRITE":
			categories.add("financial_action")
	elif root == "capabilities":
		capability_value = after if isinstance(after, dict) else before
		if isinstance(capability_value, dict) and capability_value.get("action_type") in {"WRITE", "EXECUTE"}:
			categories.add("financial_action")
		if path.endswith("/enabled") and after is True:
			categories.add("financial_action")
		if path.endswith("/action_type") and after in {"WRITE", "EXECUTE"}:
			categories.add("financial_action")
	elif root == "limits" and "max_transaction_usd" in parts:
		if after not in (None, "0", 0):
			categories.add("financial_action")
	elif root == "approval":
		categories.add("human_approval")
	elif root == "model" or root == "system_prompt_sha256":
		categories.add("model_or_prompt_change")
	elif root == "autonomy_level":
		categories.add("autonomy_change")
	return sorted(categories)


def diff_manifests(baseline: AgentManifest, candidate: AgentManifest) -> ManifestDiff:
	if baseline.agent_id != candidate.agent_id:
		raise ValueError("baseline and candidate manifests must share agent_id")
	baseline_data = json.loads(baseline.model_dump_json())
	candidate_data = json.loads(candidate.model_dump_json())
	changes = []
	for path, change_type, before, after in _walk_changes(baseline_data, candidate_data):
		changes.append(
			ManifestChange(
				path=path,
				change_type=change_type,
				before=before,
				after=after,
				risk_categories=_risk_categories(path, before, after),
			)
		)
	changes.sort(key=lambda change: (change.path, change.change_type))
	risk_categories = sorted(
		{
			category
			for change in changes
			for category in change.risk_categories
			if category in RISK_CATEGORIES
		}
	)
	return ManifestDiff(
		baseline_release_id=baseline.release_id,
		candidate_release_id=candidate.release_id,
		changes=changes,
		confirmed_risk_categories=risk_categories,
	)


def compare_manifest_paths(
	baseline_path: str | Path, candidate_path: str | Path
) -> ManifestDiff:
	return diff_manifests(load_manifest(baseline_path), load_manifest(candidate_path))
