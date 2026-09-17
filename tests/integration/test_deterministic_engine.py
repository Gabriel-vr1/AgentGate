import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from agentgate.schemas import (
    AgentManifest,
    EvaluationCase,
    ReleasePolicy,
    RiskTaxonomy,
    TestResultBundle as ResultBundleSchema,
    TestStatus as ResultStatus,
)
from agentgate.tools.manifest_tools import compare_manifest_paths, load_manifest
from agentgate.tools.policy_tools import deterministic_review_paths
from agentgate.tools.test_tools import (
    EvidenceReferenceError,
    all_required_tests_pass,
    load_catalogue,
    load_result_bundle,
    resolve_json_pointer,
    validate_result_bundle,
)

ROOT = Path(__file__).parents[2]
BASELINE = ROOT / "data/manifests/baseline_agent.json"
POLICY = ROOT / "data/policies/release_policy.json"
CATALOGUE = ROOT / "data/test_catalogue.json"


def test_controlled_json_and_jsonl_files_validate():
    manifests = [
        load_manifest(ROOT / "data/manifests/baseline_agent.json"),
        load_manifest(ROOT / "data/manifests/unsafe_candidate.json"),
        load_manifest(ROOT / "data/manifests/safe_candidate.json"),
        load_manifest(ROOT / "data/manifests/incomplete_candidate.json"),
    ]
    policy = ReleasePolicy.model_validate_json(POLICY.read_text())
    taxonomy = RiskTaxonomy.model_validate_json(
        (ROOT / "data/policies/risk_taxonomy.json").read_text()
    )
    catalogue = load_catalogue(CATALOGUE)

    assert all(manifest.agent_id == manifests[0].agent_id for manifest in manifests)
    assert len(policy.controls) == 8
    assert len(taxonomy.categories) == 7
    assert len(catalogue.tests) == 10
    for result_path in (ROOT / "data/test_results").glob("*.json"):
        load_result_bundle(result_path)
    for line in (ROOT / "evaluation/demo_cases.jsonl").read_text().splitlines():
        EvaluationCase.model_validate_json(line)


def test_unsafe_candidate_has_exactly_six_seeded_risk_categories():
    diff = compare_manifest_paths(
        BASELINE, ROOT / "data/manifests/unsafe_candidate.json"
    )

    assert diff.confirmed_risk_categories == [
        "external_side_effect",
        "financial_action",
        "human_approval",
        "model_or_prompt_change",
        "permission_change",
        "tool_change",
    ]


def test_manifest_diff_is_reproducible_and_pointers_resolve():
    first = compare_manifest_paths(BASELINE, ROOT / "data/manifests/safe_candidate.json")
    second = compare_manifest_paths(BASELINE, ROOT / "data/manifests/safe_candidate.json")

    assert first == second
    candidate = json.loads(
        (ROOT / "data/manifests/safe_candidate.json").read_text()
    )
    for change in first.changes:
        if change.path:
            resolve_json_pointer(candidate, change.path)


def test_invalid_evidence_reference_fails():
    manifest = load_manifest(BASELINE)
    catalogue = load_catalogue(CATALOGUE)
    policy = ReleasePolicy.model_validate_json(POLICY.read_text())
    bundle = ResultBundleSchema(
        schema_version="1.0",
        release_id=manifest.release_id,
        results=[
            {
                "result_id": "invalid-reference",
                "test_id": "read-only-regression",
                "status": "PASS",
                "evidence_refs": ["test:does-not-exist"],
            }
        ],
    )

    with pytest.raises(EvidenceReferenceError):
        validate_result_bundle(bundle, catalogue, manifest, policy)


def test_duplicate_results_fail():
    with pytest.raises(ValidationError):
        ResultBundleSchema(
            schema_version="1.0",
            release_id="safe-candidate-1",
            results=[
                {
                    "result_id": "duplicate-result",
                    "test_id": "read-only-regression",
                    "status": "PASS",
                    "evidence_refs": ["test:read-only-regression"],
                },
                {
                    "result_id": "duplicate-result",
                    "test_id": "approval-enforcement",
                    "status": "PASS",
                    "evidence_refs": ["test:approval-enforcement"],
                },
            ],
        )


def test_error_and_not_run_never_count_as_pass():
    bundle = ResultBundleSchema(
        schema_version="1.0",
        release_id="incomplete-candidate-1",
        results=[
            {
                "result_id": "error-result",
                "test_id": "approval-enforcement",
                "status": ResultStatus.ERROR,
                "evidence_refs": ["test:approval-enforcement"],
            },
            {
                "result_id": "not-run-result",
                "test_id": "transaction-limits",
                "status": ResultStatus.NOT_RUN,
                "evidence_refs": ["test:transaction-limits"],
            },
        ],
    )

    assert not all_required_tests_pass(
        ["approval-enforcement", "transaction-limits"], bundle
    )


def test_three_demo_cases_match_expected_verdicts():
    for line in (ROOT / "evaluation/demo_cases.jsonl").read_text().splitlines():
        case = EvaluationCase.model_validate_json(line)
        candidate_name = Path(case.candidate_manifest_path).stem
        result = deterministic_review_paths(
            ROOT / case.baseline_manifest_path,
            ROOT / case.candidate_manifest_path,
            POLICY,
            CATALOGUE,
            ROOT / f"data/test_results/{candidate_name}.json",
        )
        assert result.verdict is case.expected_verdict


def test_block_floor_cannot_be_downgraded():
    unsafe = deterministic_review_paths(
        BASELINE,
        ROOT / "data/manifests/unsafe_candidate.json",
        POLICY,
        CATALOGUE,
        ROOT / "data/test_results/unsafe_candidate.json",
    )

    assert unsafe.verdict.value == "BLOCK"


def test_policy_references_are_controlled():
    policy = ReleasePolicy.model_validate_json(POLICY.read_text())
    taxonomy = RiskTaxonomy.model_validate_json(
        (ROOT / "data/policies/risk_taxonomy.json").read_text()
    )
    catalogue = load_catalogue(CATALOGUE)
    risk_ids = {category.risk_id for category in taxonomy.categories}
    test_ids = {test.test_id for test in catalogue.tests}

    assert all(
        set(control.trigger_categories) <= risk_ids
        and set(control.required_test_ids) <= test_ids
        for control in policy.controls
    )
    assert all(set(test.risk_ids) <= risk_ids for test in catalogue.tests)
