from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import (
	AfterValidator,
	BaseModel,
	ConfigDict,
	Field,
	StringConstraints,
	model_validator,
)


class FrozenModel(BaseModel):
	model_config = ConfigDict(
		extra="forbid",
		frozen=True,
		validate_assignment=True,
	)


class Verdict(StrEnum):
	APPROVE = "APPROVE"
	CONDITIONAL = "CONDITIONAL"
	BLOCK = "BLOCK"


class RiskSeverity(StrEnum):
	LOW = "LOW"
	MEDIUM = "MEDIUM"
	HIGH = "HIGH"
	CRITICAL = "CRITICAL"


class AccessMode(StrEnum):
	NONE = "NONE"
	READ = "READ"
	WRITE = "WRITE"


class ActionType(StrEnum):
	ADVISORY = "ADVISORY"
	READ = "READ"
	WRITE = "WRITE"
	EXECUTE = "EXECUTE"


class AutonomyLevel(StrEnum):
	ADVISORY = "ADVISORY"
	ASSISTED = "ASSISTED"
	AUTONOMOUS = "AUTONOMOUS"


class TestStatus(StrEnum):
	PASS = "PASS"
	FAIL = "FAIL"
	ERROR = "ERROR"
	NOT_RUN = "NOT_RUN"


Identifier = Annotated[
	str,
	StringConstraints(
		min_length=2,
		max_length=64,
		pattern=r"^[a-z][a-z0-9_-]*$",
	),
]


def _reject_blank(value: str) -> str:
	if not value.strip():
		raise ValueError("must not be blank")
	return value


NonEmptyString = Annotated[
	str,
	StringConstraints(min_length=1),
	AfterValidator(_reject_blank),
]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


def _unique_ids(values: list[object], field_name: str) -> None:
	ids = [getattr(value, field_name) for value in values]
	if len(ids) != len(set(ids)):
		raise ValueError(f"{field_name} values must be unique")


class ModelSpec(FrozenModel):
	provider: NonEmptyString
	deployment_name: NonEmptyString
	temperature: float = Field(ge=0, le=2)


class ToolSpec(FrozenModel):
	tool_id: Identifier
	name: NonEmptyString
	description: NonEmptyString
	action_type: ActionType
	side_effects: bool
	requires_confirmation: bool


class PermissionSpec(FrozenModel):
	permission_id: Identifier
	resource: NonEmptyString
	access_mode: AccessMode
	scopes: list[NonEmptyString] = Field(min_length=1)


class CapabilitySpec(FrozenModel):
	capability_id: Identifier
	description: NonEmptyString
	action_type: ActionType
	enabled: bool


class ApprovalSpec(FrozenModel):
	human_approval_required: bool
	enforced_by: Literal["NONE", "WORKFLOW", "TOOL"]
	required_for_actions: list[Identifier]

	@model_validator(mode="after")
	def validate_approval_requirements(self) -> "ApprovalSpec":
		if self.human_approval_required:
			if self.enforced_by == "NONE" or not self.required_for_actions:
				raise ValueError(
					"required approval must have an enforcer and required actions"
				)
		elif self.enforced_by != "NONE" or self.required_for_actions:
			raise ValueError(
				"approval without human approval must use NONE and have no required actions"
			)
		return self


class OperationalLimits(FrozenModel):
	currency: Literal["USD"]
	max_transaction_usd: Decimal = Field(ge=0)
	max_actions_per_run: int = Field(ge=1)


class AgentManifest(FrozenModel):
	schema_version: Literal["1.0"]
	agent_id: Identifier
	release_id: Identifier
	display_name: NonEmptyString
	version: NonEmptyString
	description: NonEmptyString
	model: ModelSpec
	system_prompt_sha256: Sha256
	tools: list[ToolSpec]
	permissions: list[PermissionSpec]
	capabilities: list[CapabilitySpec]
	autonomy_level: AutonomyLevel
	approval: ApprovalSpec
	limits: OperationalLimits

	@model_validator(mode="after")
	def validate_unique_ids(self) -> "AgentManifest":
		_unique_ids(self.tools, "tool_id")
		_unique_ids(self.permissions, "permission_id")
		_unique_ids(self.capabilities, "capability_id")
		return self


class PolicyControl(FrozenModel):
	control_id: Identifier
	title: NonEmptyString
	description: NonEmptyString
	severity: RiskSeverity
	non_overridable: bool
	trigger_categories: list[Identifier] = Field(min_length=1)
	required_test_ids: list[Identifier]
	missing_evidence_verdict: Verdict


class ReleasePolicy(FrozenModel):
	schema_version: Literal["1.0"]
	policy_id: Identifier
	version: NonEmptyString
	description: NonEmptyString
	controls: list[PolicyControl] = Field(min_length=1)

	@model_validator(mode="after")
	def validate_unique_control_ids(self) -> "ReleasePolicy":
		_unique_ids(self.controls, "control_id")
		return self


class RiskCategory(FrozenModel):
	risk_id: Identifier
	title: NonEmptyString
	description: NonEmptyString
	default_severity: RiskSeverity


class RiskTaxonomy(FrozenModel):
	schema_version: Literal["1.0"]
	taxonomy_id: Identifier
	version: NonEmptyString
	categories: list[RiskCategory] = Field(min_length=1)

	@model_validator(mode="after")
	def validate_unique_risk_ids(self) -> "RiskTaxonomy":
		_unique_ids(self.categories, "risk_id")
		return self


class AssuranceTest(FrozenModel):
	test_id: Identifier
	title: NonEmptyString
	description: NonEmptyString
	risk_ids: list[Identifier] = Field(min_length=1)
	deterministic: bool
	required_evidence: list[NonEmptyString] = Field(min_length=1)


class TestCatalogue(FrozenModel):
	schema_version: Literal["1.0"]
	catalogue_id: Identifier
	version: NonEmptyString
	tests: list[AssuranceTest] = Field(min_length=1)

	@model_validator(mode="after")
	def validate_unique_test_ids(self) -> "TestCatalogue":
		_unique_ids(self.tests, "test_id")
		return self


class EvaluationCase(FrozenModel):
	case_id: Identifier
	title: NonEmptyString
	baseline_manifest_path: NonEmptyString
	candidate_manifest_path: NonEmptyString
	expected_verdict: Verdict
	expected_control_ids: list[Identifier]
	expected_required_test_ids: list[Identifier]
	result_bundle_path: NonEmptyString | None = None


class ManifestChange(FrozenModel):
	path: NonEmptyString
	change_type: Literal["added", "removed", "modified"]
	before: Any = None
	after: Any = None
	risk_categories: list[Identifier]


class ManifestDiff(FrozenModel):
	baseline_release_id: Identifier
	candidate_release_id: Identifier
	changes: list[ManifestChange]
	confirmed_risk_categories: list[Identifier]


class PolicyFinding(FrozenModel):
	control_id: Identifier
	triggered: bool
	verdict_floor: Verdict
	message: NonEmptyString
	required_test_ids: list[Identifier]


class PolicyEvaluation(FrozenModel):
	verdict_floor: Verdict
	findings: list[PolicyFinding]
	required_test_ids: list[Identifier]
	missing_evidence_test_ids: list[Identifier]


class TestResult(FrozenModel):
	result_id: Identifier
	test_id: Identifier
	status: TestStatus
	evidence_refs: list[NonEmptyString]


class TestResultBundle(FrozenModel):
	schema_version: Literal["1.0"]
	release_id: Identifier
	results: list[TestResult]

	@model_validator(mode="after")
	def validate_unique_result_ids(self) -> "TestResultBundle":
		_unique_ids(self.results, "result_id")
		_unique_ids(self.results, "test_id")
		return self


EvidenceReference = Annotated[
	str,
	StringConstraints(
		min_length=2,
		pattern=r"^(\/.*|control:[a-z][a-z0-9_-]*|test:[a-z][a-z0-9_-]*)$",
	),
]


class ChangeAssessmentItem(FrozenModel):
	path: NonEmptyString
	change_type: Literal["added", "removed", "modified"]
	area: Literal[
		"capability",
		"permission",
		"data_access",
		"autonomy",
		"approval",
		"model",
		"prompt",
		"metadata",
	]
	before: Any = None
	after: Any = None
	explanation: NonEmptyString
	evidence_refs: list[EvidenceReference] = Field(min_length=1)


class ChangeAssessment(FrozenModel):
	schema_version: Literal["1.0"]
	execution_mode: Literal["local_deterministic"]
	baseline_release_id: Identifier
	candidate_release_id: Identifier
	changes: list[ChangeAssessmentItem]
	confirmed_risk_categories: list[Identifier]
	summary: NonEmptyString


class AssurancePlan(FrozenModel):
	schema_version: Literal["1.0"]
	execution_mode: Literal["local_deterministic"]
	candidate_release_id: Identifier
	confirmed_risk_categories: list[Identifier]
	control_ids: list[Identifier]
	required_test_ids: list[Identifier]
	missing_evidence_test_ids: list[Identifier]
	human_review_required: bool
	rationale: NonEmptyString
	evidence_refs: list[EvidenceReference]


class DecisionFinding(FrozenModel):
	code: Identifier
	message: NonEmptyString
	evidence_refs: list[EvidenceReference] = Field(min_length=1)


class ReleaseDecision(FrozenModel):
	schema_version: Literal["1.0"]
	execution_mode: Literal["local_deterministic"]
	baseline_release_id: Identifier
	candidate_release_id: Identifier
	verdict: Verdict
	verdict_floor: Verdict
	blockers: list[DecisionFinding]
	conditions: list[DecisionFinding]
	evidence_refs: list[EvidenceReference]
	remediation: list[NonEmptyString]

	@model_validator(mode="after")
	def validate_verdict_floor(self) -> "ReleaseDecision":
		ranks = {Verdict.APPROVE: 0, Verdict.CONDITIONAL: 1, Verdict.BLOCK: 2}
		if ranks[self.verdict] < ranks[self.verdict_floor]:
			raise ValueError("verdict cannot be less severe than verdict_floor")
		return self


class WorkflowFailure(FrozenModel):
	status: Literal["FAILED"]
	stage: Literal[
		"input_validation",
		"change_analyst",
		"assurance_planner",
		"deterministic_policy",
		"release_judge",
	]
	message: NonEmptyString


class DeterministicReviewResult(FrozenModel):
	baseline_release_id: Identifier
	candidate_release_id: Identifier
	verdict: Verdict
	diff: ManifestDiff
	policy: PolicyEvaluation
	result_ids: list[Identifier]
