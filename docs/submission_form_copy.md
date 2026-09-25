# Submission form copy

## Project title
AgentGate - Evidence Before Authority

## One-sentence summary
AgentGate combines three Foundry-backed model stages with deterministic Python
controls to review synthetic agent release changes before granting authority.

## Short project description
AgentGate compares baseline and candidate manifests, highlights authority
changes, checks controlled policy and stored assurance evidence, and presents
APPROVE, CONDITIONAL or BLOCK with required remediation. A compact reviewer
provides inspectable evidence and a downloadable review record. All three
demonstration scenarios have verified live Foundry runs.

## Problem statement
Agent upgrades can silently acquire write permissions, action tools or higher
transaction limits while removing human approval. Reviewers need evidence about
changed authority, not simply a plausible explanation.

## Solution
Exact Python diffs and policy checks establish authoritative facts. Change
Analyst, Assurance Planner and Release Judge provide constrained model reasoning.
Python validates structured handoffs, evidence references and final verdicts.
Hard policy blockers cannot be downgraded by model output.

## Innovation
The design separates advisory model explanations from authoritative release
fields. Passing stored assurance results cannot override deterministic policy
blockers; the unsafe demonstration makes that distinction visible.

## Usability
The local reviewer offers fixed scenarios, explicit local/live modes, a prominent
decision, readable changes, expandable evidence, remediation and downloadable
review/trace JSON. A CLI supports reproduction.

## Impact
AgentGate is intended to help owners identify authority expansion and demand
remediation. The synthetic unsafe case blocks order-placement authority,
brokerage WRITE access and a USD 5,000 limit when approval is removed. No
commercial savings or real-world prevention rate has been measured.

## Microsoft Foundry usage
Three Foundry-backed model stages use project-scoped Responses calls through
the Azure AI Projects SDK and an existing gpt-4.1-mini deployment. Nine live
stage calls across three scenarios validated on their first attempt. These are
not persistent agent resources. Traces are local JSON, not Azure Monitor or
Application Insights exports.

## Technical architecture
Reviewer/CLI - Python validation and exact diff - Change Analyst - Assurance
Planner - deterministic policy and assurance engine - Release Judge - verdict
and reference guard - auditable decision. Python validates every handoff;
the diagram shows responsibilities rather than every internal function call.

## Responsible AI / safety
Strict Pydantic contracts, controlled input evidence and test selection, one
repair maximum per stage, reference validation and safe failure constrain the
workflow. Python owns decision fields; model prose remains advisory. Human
release owners remain accountable. Local mode is explicitly labelled.

## Limitations
Stored fixtures are not fresh candidate-agent tests. Fixed mapping and repeated
manifests limit coverage. Model prose can be wrong, including unsupported test
commentary in the saved safe case. Persistent agents, portal telemetry, formal
Foundry evaluation, hosted authentication and production deployment are deferred.

## Verification
53 automated tests; 13/13 repository evaluations (10 labelled cases + 3 demos).
Verified live outcomes: unsafe BLOCK, safe APPROVE, incomplete CONDITIONAL.
These are repository evaluations, not Foundry evaluator jobs.

## GitHub
https://github.com/Gabriel-vr1/AgentGate

## Demonstration instructions
Follow README setup; run `.venv/Scripts/python.exe app.py serve`, then open
http://127.0.0.1:8765. Select unsafe and local or configured Microsoft Foundry live
mode. Run review, inspect BLOCK, authority changes and remediation, then download
the record. Saved live evidence is linked in README. Upload the final recording
separately and provide an accessible viewing URL.
