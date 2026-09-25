# AgentGate recording script - target 2:50

339 spoken words; at 135 words/minute plus about 19 seconds of pauses, 2:50. Target 2:40-2:55 at a natural
pace. This is an estimate, not a completed spoken rehearsal. Rehearse once.
Follow [recording shot list](recording_shot_list.md); do not read headings.

## 0:00-0:20 - The problem

An agent upgrade can look routine while quietly gaining permission to act.
AgentGate helps a release reviewer answer a specific question: does this
candidate have enough evidence to receive that authority? It compares releases,
checks policy and assurance evidence, and makes the decision inspectable.

## 0:20-0:45 - Start the live review

Here is the unsafe authority expansion scenario. I select Microsoft Foundry
live and run the review. These are three Foundry-backed model stages:
Change Analyst explains the supplied changes, Assurance Planner explains the
controlled assurance plan, and Release Judge recommends a verdict. They are
application stages, not persistent portal agents.

## 0:45-1:15 - Why BLOCK

The result is BLOCK. The candidate adds an order-placement tool, changes
brokerage access from READ to WRITE, raises transaction authority from zero
to five thousand dollars, and removes mandatory human approval. The reviewer
shows the baseline and candidate, confirmed authority changes, and two hard
policy blockers. Required remediation makes the reason for stopping this
release concrete.

## 1:15-1:45 - Safety and evidence

Python owns the exact diff, test selection, evidence validation and verdict
floor. Model output cannot downgrade validated policy blockers. Strict
Pydantic handoffs permit at most one repair per stage; invalid cloud output
stops the review. These ten selected stored assurance results pass, but
passing evidence cannot override a hard policy blocker. They are fixtures,
not newly executed trading-agent tests.

## 1:45-2:15 - Auditability and other outcomes

The audit record exposes the execution mode, timing and trace identifier.
I can download the review and trace. This is local structured application
tracing with Foundry response identifiers, not Azure Monitor. Saved live
evidence also shows the safe bounded improvement receiving APPROVE and the
missing-evidence case receiving CONDITIONAL. All nine live stage calls
succeeded on their first attempt.

## 2:15-2:50 - Verification and distinction

The repository passes fifty-three automated tests and all thirteen evaluation
cases: ten labelled cases and three demonstrations. Local deterministic mode
remains available. This is a synthetic, bounded demonstration: model prose is
advisory, policy coverage is fixed, and no real trading occurs. Formal Foundry
evaluation and portal telemetry are deferred. The release owner remains
accountable. AgentGate's distinction is evidence before authority: inspect the
change, enforce the policy, and require remediation before approving the release.

---

If live latency prevents this sequence, use the explicitly labelled saved-run
alternative in the shot list. Replace the live-run introduction with: "This is
the saved record of the verified live Foundry run." Never present replay as live.
