import json
from pathlib import Path
from typing import Any

from agentgate.schemas import (
	AgentManifest,
	PolicyEvaluation,
	ReleasePolicy,
	TestCatalogue,
	TestResultBundle,
)


class EvidenceReferenceError(ValueError):
	"""Raised when stored evidence does not resolve to a controlled object."""


def load_catalogue(path: str | Path) -> TestCatalogue:
	with Path(path).open(encoding="utf-8") as handle:
		return TestCatalogue.model_validate(json.load(handle))


def load_result_bundle(path: str | Path) -> TestResultBundle:
	with Path(path).open(encoding="utf-8") as handle:
		return TestResultBundle.model_validate(json.load(handle))


def resolve_json_pointer(document: Any, pointer: str) -> Any:
	if pointer == "":
		return document
	if not pointer.startswith("/"):
		raise EvidenceReferenceError(f"invalid JSON Pointer: {pointer}")
	value = document
	for token in pointer[1:].split("/"):
		token = token.replace("~1", "/").replace("~0", "~")
		try:
			if isinstance(value, list):
				value = value[int(token)]
			else:
				value = value[token]
		except (KeyError, IndexError, TypeError, ValueError) as error:
			raise EvidenceReferenceError(
				f"JSON Pointer does not resolve: {pointer}"
			) from error
	return value


def validate_result_bundle(
	bundle: TestResultBundle,
	catalogue: TestCatalogue,
	manifest: AgentManifest,
	policy: ReleasePolicy,
) -> TestResultBundle:
	if bundle.release_id != manifest.release_id:
		raise EvidenceReferenceError("result bundle release_id does not match manifest")
	test_ids = {test.test_id for test in catalogue.tests}
	control_ids = {control.control_id for control in policy.controls}
	manifest_document = json.loads(manifest.model_dump_json())
	for result in bundle.results:
		if result.test_id not in test_ids:
			raise EvidenceReferenceError(f"unknown test_id: {result.test_id}")
		for reference in result.evidence_refs:
			if reference.startswith("/"):
				resolve_json_pointer(manifest_document, reference)
			elif reference.startswith("control:"):
				if reference.removeprefix("control:") not in control_ids:
					raise EvidenceReferenceError(f"unknown control reference: {reference}")
			elif reference.startswith("test:"):
				if reference.removeprefix("test:") not in test_ids:
					raise EvidenceReferenceError(f"unknown test reference: {reference}")
			else:
				raise EvidenceReferenceError(f"unsupported evidence reference: {reference}")
	return bundle


def validate_evidence_references(
	references: list[str],
	manifest: AgentManifest,
	policy: ReleasePolicy,
	catalogue: TestCatalogue,
) -> list[str]:
	"""Validate references emitted by agent handoffs and final decisions."""
	control_ids = {control.control_id for control in policy.controls}
	test_ids = {test.test_id for test in catalogue.tests}
	manifest_document = json.loads(manifest.model_dump_json())
	for reference in references:
		if reference.startswith("/"):
			resolve_json_pointer(manifest_document, reference)
		elif reference.startswith("control:"):
			if reference.removeprefix("control:") not in control_ids:
				raise EvidenceReferenceError(f"unknown control reference: {reference}")
		elif reference.startswith("test:"):
			if reference.removeprefix("test:") not in test_ids:
				raise EvidenceReferenceError(f"unknown test reference: {reference}")
		else:
			raise EvidenceReferenceError(f"unsupported evidence reference: {reference}")
	return references


def result_statuses(bundle: TestResultBundle) -> dict[str, str]:
	return {result.test_id: result.status.value for result in bundle.results}


def all_required_tests_pass(
	required_test_ids: list[str], bundle: TestResultBundle
) -> bool:
	statuses = result_statuses(bundle)
	return all(statuses.get(test_id) == "PASS" for test_id in required_test_ids)
