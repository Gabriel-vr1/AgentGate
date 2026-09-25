# Blueprint audit and submission scope

Reference: **AgentGate_Project_Blueprint.pdf**, 11 pages, supplied by the owner
on 25 September 2026. This audit uses its numbered sections and page numbers.
The current owner instructions govern the deadline (09:00 SAST today), prohibit
new resources and Streamlit, and require preservation of the working integration.
The PDF's older schedule and provisioning suggestions are not execution instructions.

## Required MVP and definition of done

| Blueprint requirement | Status | Implementation / evidence |
| --- | --- | --- |
| Baseline-to-candidate workflow (2.1, 15) | Implemented | Sequential Python workflow; three CLI/UI cases |
| Three distinct specializations (5) | Implemented as model stages | Change Analyst, Assurance Planner, Release Judge; separate inputs and responsibilities |
| Persistent Foundry agents and portal runs (2.1, 4, stage 3) | Not implemented | Project-scoped Responses calls via AIProjectClient; no agent registration, persistent agent IDs, threads or hosted agent runs |
| Foundry model integration (2.1) | Verified | Existing gpt-4.1-mini deployment; three live scenarios and nine successful stage calls |
| Pydantic JSON contracts (6) | Implemented with narrower fields | ChangeAssessment, AssurancePlan, ReleaseDecision; Python builds authoritative fields around constrained model output |
| Exact diffs, schema checks, policy blockers and reference resolution (6) | Implemented for controlled cases | Python tools and workflow validators; existing deterministic behavior preserved |
| Closed evidence set and bounded test catalogue (7) | Implemented for decision fields | No web/tools available to model; controlled manifests, policy, taxonomy and stored results |
| One repair then safe stop (6, 14) | Implemented | At most one schema/verdict repair per stage; transport failure stops immediately; generic repair feedback, not detailed Pydantic error feedback |
| Non-downgrade verdict guard (3, 7) | Implemented, stricter cloud recommendation | Cloud verdict must equal Python floor; model cannot strengthen it in this version |
| Execute assurance tests during a review (6) | Partial | Reviews validate and consume stored PASS/FAIL/ERROR/NOT_RUN fixtures; they do not execute a candidate agent or generate new test results |
| Unknown high-risk capabilities always require review (6) | Partial | Unknown schema fields/enums and taxonomy IDs fail validation; semantic risk mapping is fixed and not a general detector for arbitrary capabilities |
| Complete release record with uncertainty (1.3) | Partial | Verdict, blockers, conditions, references and remediation exist; missing evidence in plan; no dedicated uncertainty field or per-claim confidence |
| Full proposed manifest / handoff field inventory (5, 6) | Partial | No separate data-source inventory, risk-hypothesis field, planner provisional-severity field, or test-result-ID reference format; permissions, confirmed risks and control/test references are supported |
| Controlled data pack (8) | Implemented | Baseline and three demo candidates, permission-removal case, 8 policy controls, 7 risk categories, 10 catalogue tests |
| At least ten labelled evaluations and three demos (8, 12) | Verified locally | 10 evaluation cases plus 3 demo cases; all 13 pass; several cases reuse manifests, so this is not 13 independent agents |
| Foundry evaluation dataset/run (4, stage 6) | Not implemented | Local Python evaluations only; live inference runs are not Foundry evaluation jobs |
| Application Insights / Foundry tracing (2.1, stage 5) | Partial substitute | Local JSON spans with response IDs, usage, durations, status and final decision; no portal export, deterministic-tool spans or full serialized handoff spans |
| Trace per demo and visible failure (11, 15) | Partial | Three successful live application traces plus an explicitly mocked timeout trace; no portal trace coverage or live injected-failure claim |
| Local reviewer experience (2.1, stage 7) | Implemented, adapted technology | Standard-library HTTP server and HTML, not Streamlit; fixed scenario selection, no arbitrary manifest upload; CLI retained |
| Clean checkout, setup, architecture and demo assets (stage 8, 15) | Verified / completed | Fresh Python 3.12 venv installation and HTTP startup; README, architecture diagram, timed script, submission summary and limitations |
| No secrets, trading, deployment or extra agents (2.2, 15) | Verified within audit scope | History/current-tree secret scan and scope inspection; no Azure resources created |
| Existing challenge fork layout (9) | Adapted | Standalone AgentGate repository, not a subfolder of the official examples fork |
| Final recording and submission receipt (13) | Owner action remaining | Script and runnable application supplied; no recording or portal submission claimed |

## Measured quality targets (section 11)

| Target | Measured result / qualification |
| --- | --- |
| Verdict accuracy >=90% on >=10 cases | 10/10 labelled local evaluations; 3/3 separate demo labels also pass |
| Critical blocker recall 100% | All six BLOCK-labelled evaluation cases return BLOCK; they reuse the unsafe manifest, so this is seeded-case recall only |
| Structured-output validity | All nine successful live stage outputs accepted on attempt 1; assembled handoffs pass Pydantic/workflow validation |
| Evidence-reference validity | Workflow validation passes for all 13 local cases and three live cases; this establishes resolvable supported references, not independent evidence truth |
| Zero unsupported material claims | Authoritative decision fields are Python-owned; zero unsupported narrative claims is NOT established. Safe live planner/judge prose mentions tests not selected by Python |
| 3/3 workflow reliability | Three live CLI scenarios completed in this sprint; fresh-clone local HTTP scenarios also completed |
| Complete portal trace coverage | Not met; application-level JSON traces only |
| Verdict in <=3 actions | Fixed scenario selection, Run review, inspect result; HTTP verified, browser visual/action-count verification unavailable |

The original blueprint is therefore **partially fulfilled**, not fully complete.
Persistent resources, portal telemetry/evaluation, general policy coverage and
fully grounded model prose remain explicit gaps. They are deferred under the
owner's submission freeze rather than represented as completed work.

## Original implementation request cross-check

The owner's prior 16-item implementation request is satisfied at the application
level: optional compatible SDK dependencies; non-secret configuration; no committed
credentials; three Foundry-backed interfaces; Pydantic handoffs; one repair limit;
local fallback; BLOCK floor; safe failure; local structured tracing; mocked tests;
live unsafe verification (now all three cases); compact reviewer; documentation;
complete tests/evaluations; and committed/pushed checkpoints. Item 10 is local
application tracing, not the stronger portal-tracing requirement in the blueprint.
