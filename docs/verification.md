# Submission verification ? 25 September 2026

## Live Foundry evidence

Existing project: `agentgate`; resource: `agentgate-foundry-gvr0710`;
region: Spain Central; deployment: `gpt-4.1-mini`.
Authentication used the existing Azure CLI session. No resources were created,
removed, or reconfigured. No keys or tokens were committed.

The saved unsafe run began at `2026-09-25T04:39:04.604589+00:00` and completed
all three stages on their first attempts. The result was BLOCK with Python
floor BLOCK. [Trace](evidence/unsafe-foundry-trace.json),
[decision](evidence/unsafe-foundry-decision.json).

| Stage | Response ID | Duration |
| --- | --- | --- |
| Change Analyst | `resp_0858550130aad028016ab5faec50248190ad61a464ebb3d40b` | 5229.39 ms |
| Assurance Planner | `resp_09560f245f78af2c016ab5faefca5481969ee70e4ff0116083` | 2432.15 ms |
| Release Judge | `resp_0c10f42f858cdf5c016ab5faf258bc81978918aab8670239d9` | 2355.80 ms |

Total recorded usage: 9,335 tokens across three responses. The trace records
application spans and service response IDs, not Azure Monitor export. Responses
were requested with `store=False`.

## Automated checks

- Full pytest suite: **53 passed** (including all 34 original tests).
- Evaluation suites: **13/13 passed**, including verdict, expected control subset
  and expected required-test subset checks. [Results](evidence/evaluation-results.json).
- Three local CLI demonstrations: unsafe BLOCK, safe APPROVE, incomplete CONDITIONAL.
- `pip check`: no broken requirements.
- Mocked cloud checks: all three scenarios, bounded repair, wrong verdict,
  extra/invented fields, blank output, timeout, sanitized error logging,
  credential-destination validation, and preservation of Python findings.
- Reviewer HTTP checks: HTML served, complete scenario evidence returned, and
  cross-origin review requests rejected.

The incomplete demo case previously expected `authority-requires-approval`
although the baseline engine does not emit that finding for that case. Its
expectation now matches the existing deterministic behavior and evaluation case;
policy semantics were not changed.

## Limitations

No browser was available to the automation session, so visual layout and browser
interaction have not been verified. The live unsafe case was verified through
the CLI, not through the browser. Other cloud scenarios are mocked, not live.
No Azure portal trace visibility or telemetry export was verified or configured.
The stored tests are synthetic fixtures. Model narratives can still overstate
what a PASS fixture proves; they never change the authoritative decision fields.

Verified runtime packages include Python 3.12, azure-ai-projects 2.7.0,
azure-identity 1.25.3 and its compatible transitive OpenAI client 3.19.2.
