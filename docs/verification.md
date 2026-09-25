# Submission verification - 25 September 2026

## Live Foundry results

All three cases completed through all three stages using the existing project
`agentgate`, resource `agentgate-foundry-gvr0710`, deployment `gpt-4.1-mini`.
No resources were created or changed. These are project-scoped model calls,
not persistent agents or formal Foundry evaluation jobs.

| Scenario | Verdict | Start (UTC; add 2h for SAST) | Model-call time | Tokens |
| --- | --- | --- | --- | --- |
| unsafe | BLOCK | 2026-09-25T04:55:02.142504+00:00 | 11.57 s | 9321 |
| safe | APPROVE | 2026-09-25T04:55:15.783188+00:00 | 8.32 s | 5121 |
| incomplete | CONDITIONAL | 2026-09-25T04:55:25.968241+00:00 | 7.98 s | 4948 |

All nine model outputs validated on attempt 1; no repair was required. The three
runs finished within one minute, well inside the 30-minute live-run limit.
Model-call time is the sum of recorded request durations, not a benchmark or
end-to-end browser latency measurement.

## Evidence index

- [Unsafe trace](evidence/unsafe-foundry-trace.json) and [decision](evidence/unsafe-foundry-decision.json)
- [Safe trace](evidence/safe-foundry-trace.json) and [decision](evidence/safe-foundry-decision.json)
- [Incomplete trace](evidence/incomplete-foundry-trace.json) and [decision](evidence/incomplete-foundry-decision.json)
- [Live summary](evidence/live-run-summary.json): response IDs, source/input hashes, timings and usage
- [Mocked failure trace](evidence/mocked-failure-trace.json): injected timeout, safe stop, no decision; NOT a live service failure
- [Labelled evaluation results](evidence/evaluation-results.json)
- [Secret scan report](evidence/secret-scan.json)
- [Clean-clone verification](evidence/clean-clone-verification.json)

These traces are local application JSON. There is no Azure Monitor/Application
Insights export, portal-trace verification, or tool/handoff span coverage.
Optional portal tracing/evaluation work was deferred without provisioning or
changing the existing integration.

## Tests and metrics

- Full pytest suite: **53 passed**, including all 34 original tests.
- Labelled evaluation suite: **10/10**, including all six BLOCK-labelled cases.
- Demonstration suite: **3/3**. Both suites check verdicts, expected control
  subsets and selected-test subsets; workflow execution validates references.
- Three local CLI demos: **BLOCK / APPROVE / CONDITIONAL**.
- Fresh Python 3.12 clone installation and reviewer HTTP startup: passed.
- Fresh-clone local review API: all three expected verdicts returned.
- JavaScript syntax (`node --check`), dependency consistency (`pip check`) and
  local Markdown link checks: passed.

The copied `.env` exposed a configuration-test isolation bug. The test fixture
now changes to a temporary directory, so developer settings do not alter the
safe-defaults test. Application configuration and business logic are unchanged.

## Qualification of blueprint metrics

Schema-valid output and resolvable references do not prove narrative truth.
The saved safe planner/judge commentary mentions tests that Python did not
select. The authoritative selected-test list is empty and the final decision
retains only Python-owned fields. Zero unsupported model claims is not claimed.
Six BLOCK-labelled evaluation cases reuse the unsafe manifest; 100% seeded
recall does not establish general policy coverage. Stored PASS/FAIL/ERROR/NOT_RUN
results are fixtures, not newly executed candidate tests.

Browser automation exposed no browser. Visual layout, click-through behavior
and download interactions were not verified. The 180-second demo script is a
recording plan; a timed spoken rehearsal and final recording remain owner actions.
See the [blueprint audit](blueprint-audit.md) and [limitations](limitations.md).
