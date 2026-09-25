# Three-minute demonstration script

## Prepare before recording

Use the exact setup commands in the README. Set the Foundry environment
variables, confirm the Azure CLI session is authenticated, and start:

```powershell
.venv/Scripts/python.exe app.py serve
```

Open http://127.0.0.1:8765. Select Microsoft Foundry live-model mode.
Keep the [evidence index](verification.md) open in another tab or editor.
The three saved runs took approximately 8-12 seconds of model time each;
allow extra time for network variability. This is a 180-second recording plan,
not a claim that a full spoken browser rehearsal was timed in this session.

## Recording timeline

| Time | Action | Suggested narration |
| --- | --- | --- |
| 0:00-0:20 | Show the scenario selector and Foundry mode | AgentGate asks what authority changed, what evidence is needed, and whether a human should release the candidate. Everything here is synthetic. |
| 0:20-1:00 | Run Unsafe authority expansion; point to the diff and BLOCK | This upgrade adds an order tool, WRITE access and a USD 5,000 limit while removing human approval. Python blocks it even though stored fixtures say PASS. |
| 1:00-1:30 | Show findings, remediation and the three stage explanations; expand trace | Change Analyst explains the diff, Assurance Planner explains controlled test selection, and Release Judge recommends a constrained verdict. Python owns authoritative fields. These are Foundry-backed model stages, not persistent agents. |
| 1:30-2:00 | Run Safe bounded improvement in Foundry mode | This bounded advisory change returns APPROVE. Python selects no required tests for this scenario. Model commentary is advisory, so the selected-test table takes precedence over prose. |
| 2:00-2:30 | Run Missing assurance evidence in Foundry mode | This case returns CONDITIONAL: required approval and transaction-limit evidence is not passing. Missing evidence never becomes a pass. |
| 2:30-3:00 | Download review plus trace; show local mode selector and evidence index | All three cases have saved live response IDs and decisions. Local deterministic mode remains available. Traces and evaluations are local, not Application Insights or Foundry evaluation jobs. A human remains accountable for release. |

## If service latency threatens the recording

Use the already saved traces and decisions and label them **recorded live runs**.
Run the UI in visibly labelled local mode to keep the walkthrough responsive.
Do not present local output or a saved artifact as a new live execution.

## CLI backup

```powershell
.venv/Scripts/python.exe app.py run unsafe --mode foundry --save out/unsafe-decision.json --trace out/unsafe-trace.json
.venv/Scripts/python.exe app.py run safe --mode foundry --save out/safe-decision.json --trace out/safe-trace.json
.venv/Scripts/python.exe app.py run incomplete --mode foundry --save out/incomplete-decision.json --trace out/incomplete-trace.json
.venv/Scripts/python.exe app.py run all
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m agentgate.evaluation
```

## Claims to avoid

Do not claim persistent Foundry agent resources, portal traces, Application
Insights, formal Foundry evaluations, fresh execution of assurance tests,
zero model hallucinations, or completion of every original blueprint item.
Do not claim the demo was recorded or submitted until the owner has done so.
