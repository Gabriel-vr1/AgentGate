"""Evaluate controlled cases offline; expected control/test IDs are required subsets."""
import json
from pathlib import Path

from agentgate.tools.policy_tools import deterministic_review_paths
from agentgate.workflow import run_workflow


def evaluate(root):
    results = []
    for suite in ("eval_cases", "demo_cases"):
        for line in (root / f"evaluation/{suite}.jsonl").read_text().splitlines():
            case = json.loads(line)
            candidate = root / case["candidate_manifest_path"]
            evidence = root / case.get("result_bundle_path", f"data/test_results/{candidate.stem}.json")
            paths = (root / case["baseline_manifest_path"], candidate,
                     root / "data/policies/release_policy.json", root / "data/policies/risk_taxonomy.json",
                     root / "data/test_catalogue.json", evidence)
            decision = run_workflow(*paths)
            review = deterministic_review_paths(paths[0], paths[1], paths[2], paths[4], paths[5])
            checks = {
                "verdict": decision.verdict == case["expected_verdict"],
                "controls": set(case["expected_control_ids"]) <= {f.control_id for f in review.policy.findings},
                "tests": set(case["expected_required_test_ids"]) <= set(review.policy.required_test_ids),
            }
            results.append({"suite": suite, "case_id": case["case_id"], "checks": checks,
                            "passed": all(checks.values())})
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--save", type=Path)
    args = parser.parse_args()
    results = evaluate(args.root)
    output = json.dumps({"passed": sum(r["passed"] for r in results), "total": len(results), "cases": results}, indent=2)
    print(output)
    if args.save:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        args.save.write_text(output + "\n", encoding="utf-8")
    raise SystemExit(0 if all(r["passed"] for r in results) else 1)
