# AgentGate submission summary

**AgentGate: evidence before authority.**

AgentGate reviews changes to an AI agent's tools, permissions, approval rules
and financial authority before a human release owner promotes a candidate.
It combines three specialized Microsoft Foundry-backed model stages with
deterministic Python checks. The output is an auditable APPROVE, CONDITIONAL
or BLOCK decision with evidence references and required remediation.

The demonstration is entirely synthetic. The unsafe candidate gains a
side-effecting order tool, WRITE access and a USD 5,000 transaction limit while
removing human approval. Python blocks it even when stored assurance fixtures
say PASS. The bounded candidate is approved; incomplete evidence produces a
conditional result. This highlights the product's central idea: test status
alone cannot justify expanded agent authority.

## Verified submission evidence

| Live scenario | Final verdict | Evidence |
| --- | --- | --- |
| Unsafe authority expansion | BLOCK | [Trace](evidence/unsafe-foundry-trace.json) / [decision](evidence/unsafe-foundry-decision.json) |
| Safe bounded improvement | APPROVE | [Trace](evidence/safe-foundry-trace.json) / [decision](evidence/safe-foundry-decision.json) |
| Missing assurance evidence | CONDITIONAL | [Trace](evidence/incomplete-foundry-trace.json) / [decision](evidence/incomplete-foundry-decision.json) |

All three used the existing Foundry project `agentgate` and `gpt-4.1-mini`
deployment on 25 September 2026. All nine stage calls completed on their first
attempt. Tests and labelled evaluations are local; they are not Foundry
evaluation jobs. See the [verification record](verification.md) for measured results.

## What the reviewer sees

Choose a scenario, run review, inspect baseline/candidate releases, exact
authority changes, policy findings, selected tests, stored evidence, final
verdict and remediation. Expand model-stage explanations and download the
review plus local trace. Local deterministic mode remains available explicitly.

## Architecture and honest boundaries

Change Analyst explains the supplied diff. Assurance Planner explains controlled
test selection. Release Judge produces a constrained recommendation. Python owns
the authoritative fields and final guard. These are application-level
**Foundry-backed model stages**, not persistent Foundry agent resources.

Traces are local JSON with service response IDs, timing and usage. Application
Insights, portal traces and formal Foundry evaluations are not claimed. Stored
tests are fixtures; they are not newly executed candidate tests. Model prose can
contain unsupported statements and is labelled advisory. The policy engine is
limited to the controlled demonstration.

## Submission assets

- [Setup and run commands](../README.md)
- [Architecture diagram and responsibility boundaries](architecture.md)
- [Three-minute recording script](demo_script.md)
- [Blueprint requirement audit](blueprint-audit.md)
- [Limitations](limitations.md)
- [Verification and evidence index](verification.md)

The repository and script are prepared for the owner to record and submit.
No recording, challenge eligibility decision or successful portal submission
is implied by this implementation report.

## Final submission assets

See the [technical PDF](AgentGate_Technical_Architecture_and_Evidence.pdf),
[recording shot list](recording_shot_list.md), [submission form copy](submission_form_copy.md),
[consolidated blueprint status](submission-status.md) and [final verification](final-verification.md).
