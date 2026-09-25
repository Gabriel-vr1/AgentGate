# AgentGate reviewer demonstration

## Prepare

Install `.[dev,foundry]`, configure the two Foundry environment variables as shown
in the README, and start `python app.py serve`. Open http://127.0.0.1:8765.
Keep [the verified live trace](evidence/unsafe-foundry-trace.json) available as
saved evidence if connectivity is unavailable. Never present a saved trace as a
new live run.

## Three-minute walkthrough

1. **Frame the problem.** A changed agent can gain authority while its stored
   tests still say PASS. AgentGate reviews that authority expansion before release.
2. **Select Unsafe authority expansion**, choose Microsoft Foundry, and run review.
   Show baseline `baseline-1` against `unsafe-candidate-1`. Point to removal of
   workflow approval, READ-to-WRITE permission escalation, the added `place-order`
   tool and the USD 5,000 limit. These are synthetic manifests, not trading actions.
3. **Show BLOCK.** The Python floor and final verdict are both BLOCK. Point to
   `authority-requires-approval` and `financial-action-limits`. All stored test
   statuses may say PASS; those fixtures cannot override these blockers.
4. **Show the three stages.** Change Analyst explains the diff; Assurance Planner
   explains the controlled test selection; Release Judge recommends the same
   Python verdict. Model prose is advisory. Evidence and remediation remain
   Python-owned. Inspect the trace and download the review plus trace.
5. **Compare locally.** Select Local deterministic mode and run Safe bounded
   improvement (APPROVE), then Missing assurance evidence (CONDITIONAL). Local
   mode is visibly labeled and uses the same guardrails without a model call.
6. **Close with remediation.** Resolve the named policy blockers before release;
   provide missing assurance evidence where required. Human owners decide the
   subsequent release action. AgentGate does not deploy anything.

## CLI alternative

```powershell
python app.py run unsafe --mode foundry --save out/decision.json --trace out/trace.json
python app.py run unsafe
python app.py run safe
python app.py run incomplete
python -m pytest -q
python -m agentgate.evaluation
```

If Foundry fails, the run fails safely. Select local mode explicitly; do not label
that result as cloud execution. Existing saved evidence proves the recorded live
run only. Traces here are local JSON; no Foundry-portal trace visibility is claimed.
