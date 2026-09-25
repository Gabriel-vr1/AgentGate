"""One execution entry point for CLI and reviewer UI."""
from agentgate.config import get_settings
from agentgate.tracing import RunTrace
from agentgate.workflow import run_workflow


def execute(paths, mode="local_deterministic", trace_path=None):
    trace = RunTrace(mode)
    try:
        if mode == "foundry":
            from agentgate.agents.foundry import (
                connect, FoundryChangeAnalyst, FoundryAssurancePlanner, FoundryReleaseJudge,
            )
            with connect(get_settings(), trace) as session:
                decision = run_workflow(*paths, change_analyst=FoundryChangeAnalyst(session),
                                        assurance_planner=FoundryAssurancePlanner(session),
                                        release_judge=FoundryReleaseJudge(session))
        elif mode == "local_deterministic":
            decision = run_workflow(*paths)
        else:
            raise ValueError("Unknown execution mode")
        trace.finish(decision)
        return decision, trace.document
    except Exception as error:
        trace.document.update(status="FAILED", error_type=type(error).__name__)
        raise
    finally:
        if trace_path is not None:
            trace.save(trace_path)
