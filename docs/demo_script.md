# AgentGate local demonstration

## Business problem

AgentGate checks whether a changed AI agent release should be approved before
its authority expands. The demonstration uses synthetic market research data
and never places a real order.

## Run the cases

```bash
python app.py list
python app.py run unsafe
python app.py run safe
python app.py run incomplete
```

The unsafe candidate adds `place-order`, changes brokerage access to `WRITE`,
adds USD 5,000 transaction authority, and removes enforced human approval. It
must end in `BLOCK`.

## Three responsibilities

- **Change Analyst** explains the exact deterministic manifest diff.
- **Assurance Planner** maps confirmed risks to fixed controls and test IDs.
- **Release Judge** summarizes blockers, conditions, evidence, and remediation.

All three run in explicitly labelled `local_deterministic` mode. They do not
replace Python policy logic.

## Guardrails and comparison

Python validates every handoff, resolves evidence references, selects required
tests, and computes the verdict floor. A deterministic `BLOCK` cannot be
downgraded. The bounded safe candidate produces `APPROVE`; the incomplete
candidate produces `CONDITIONAL` because required evidence is not passing.

## Limitations and accountability

This is a synthetic local demonstration. It has no live model, Foundry
connection, brokerage, market data, MCP, or deployment integration. Human
owners remain accountable for reviewing evidence and the final release action.
