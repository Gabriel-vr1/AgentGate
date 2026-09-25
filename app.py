import argparse
import json
from pathlib import Path

from agentgate.tools.manifest_tools import compare_manifest_paths
from agentgate.workflow import WorkflowError
from agentgate.runner import execute


ROOT = Path(__file__).parent
CASES = {
	"unsafe": ("unsafe_candidate", "Unsafe authority expansion"),
	"safe": ("safe_candidate", "Safe bounded improvement"),
	"incomplete": ("incomplete_candidate", "Missing assurance evidence"),
}


def _paths(candidate_name: str) -> tuple[Path, ...]:
	return (
		ROOT / "data/manifests/baseline_agent.json",
		ROOT / f"data/manifests/{candidate_name}.json",
		ROOT / "data/policies/release_policy.json",
		ROOT / "data/policies/risk_taxonomy.json",
		ROOT / "data/test_catalogue.json",
		ROOT / f"data/test_results/{candidate_name}.json",
	)


def _print_decision(case_id: str, decision, diff) -> None:
	print(f"Case: {case_id}")
	print(f"Baseline: {decision.baseline_release_id}")
	print(f"Candidate: {decision.candidate_release_id}")
	print("Authority changes:")
	authority_changes = [
		change
		for change in diff.changes
		if any(
			term in change.path
			for term in ("/tools/", "/permissions/", "/capabilities/", "/approval/", "/limits/")
		)
	]
	if authority_changes:
		for change in authority_changes:
			print(f"  {change.change_type}: {change.path} -> {change.after!r}")
	else:
		print("  none")
	controls = sorted(
		reference.removeprefix("control:")
		for reference in decision.evidence_refs
		if reference.startswith("control:")
	)
	tests = sorted(
		reference.removeprefix("test:")
		for reference in decision.evidence_refs
		if reference.startswith("test:")
	)
	print(f"Selected controls: {', '.join(controls) or 'none'}")
	print(f"Selected tests: {', '.join(tests) or 'none'}")
	print(f"Deterministic verdict floor: {decision.verdict_floor.value}")
	print(f"Final verdict: {decision.verdict.value}")
	print(f"Execution mode: {decision.execution_mode}")
	print("Blockers:")
	for finding in decision.blockers:
		print(f"  - {finding.code}: {finding.message}")
	print("Conditions:")
	for finding in decision.conditions:
		print(f"  - {finding.code}: {finding.message}")
	print(f"Evidence references: {', '.join(decision.evidence_refs) or 'none'}")
	print("Remediation:")
	for item in decision.remediation:
		print(f"  - {item}")


def run_case(case_id: str, save_path: Path | None = None, mode="local_deterministic", trace_path=None) -> int:
	candidate_name, title = CASES[case_id]
	paths = _paths(candidate_name)
	try:
		decision, _ = execute(paths, mode, trace_path)
		diff = compare_manifest_paths(paths[0], paths[1])
	except (WorkflowError, ValueError) as error:
		print(f"Execution mode: {mode}")
		print(f"Case failed: {error}")
		return 2
	_print_decision(title, decision, diff)
	if save_path is not None:
		save_path.parent.mkdir(parents=True, exist_ok=True)
		save_path.write_text(
		json.dumps(decision.model_dump(mode="json"), indent=2) + "\n",
		encoding="utf-8",
	)
		print(f"Saved decision: {save_path}")
	return 0


def main() -> int:
	parser = argparse.ArgumentParser(description="AgentGate governed release assurance")
	subparsers = parser.add_subparsers(dest="command", required=True)
	subparsers.add_parser("list", help="list controlled demonstration cases")
	run_parser = subparsers.add_parser("run", help="run one controlled demonstration case")
	run_parser.add_argument("case", choices=[*CASES, "all"])
	run_parser.add_argument("--save", type=Path, help="save one final decision as JSON")
	run_parser.add_argument("--mode", choices=["local_deterministic", "foundry"], default="local_deterministic")
	run_parser.add_argument("--trace", type=Path, help="save application trace JSON")
	serve_parser = subparsers.add_parser("serve", help="open the local reviewer interface")
	serve_parser.add_argument("--port", type=int, default=8765)
	args = parser.parse_args()
	if args.command == "serve":
		from agentgate.reviewer import serve
		serve(ROOT, args.port)
		return 0
	if args.command == "list":
		for case_id, (_, title) in CASES.items():
			print(f"{case_id}: {title}")
		return 0
	if args.case == "all":
		if args.save or args.trace:
			parser.error("--save and --trace require one case")
		return max(run_case(case_id, mode=args.mode) for case_id in CASES)
	return run_case(args.case, args.save, args.mode, args.trace)


if __name__ == "__main__":
	raise SystemExit(main())
