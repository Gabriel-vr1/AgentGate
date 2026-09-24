# AgentGate

AgentGate is a multi-agent release assurance system for comparing a baseline
AI-agent release with a candidate release and producing an evidence-backed
release recommendation.

The planned assurance team is:

- **Change Analyst**: identifies meaningful changes between releases.
- **Assurance Planner**: plans the evidence needed to assess those changes.
- **Release Judge**: weighs the evidence and recommends a release outcome.

Deterministic Python owns exact comparisons, policy blockers, and verdict
floors. The system produces one of three verdicts: **APPROVE**,
**CONDITIONAL**, or **BLOCK**.

The demonstration will use a synthetic trading agent. It does not perform real
trading and excludes deployment automation and production brokerage
connections.

## Current status

The local governed workflow is implemented. Python validates the release
contracts, calculates exact diffs, selects tests, evaluates policy, validates
evidence references, and enforces the verdict floor. The three narrow agent
components produce structured local deterministic handoffs:

1. Change Analyst explains the exact diff.
2. Assurance Planner maps confirmed risks to controlled evidence.
3. Release Judge renders the decision without lowering the Python floor.

Execution is explicitly `local_deterministic`; it is not a live LLM or
Microsoft Foundry connection. Foundry-backed implementations are the next
stage and must preserve these handoff contracts and guardrails.

## Controlled demonstration

The local demonstration compares the synthetic market-research baseline with
three candidates:

- unsafe authority expansion: **BLOCK**
- safe bounded improvement: **APPROVE**
- missing assurance evidence: **CONDITIONAL**

List and run the local demonstration with:

```bash
python app.py list
python app.py run unsafe
python app.py run safe
python app.py run incomplete
python app.py run all
python app.py run unsafe --save out/unsafe-decision.json
```

The controlled cases produce `BLOCK`, `APPROVE`, and `CONDITIONAL`
respectively. No command performs real trading or provisions Azure resources.

Run the deterministic tests with:

```bash
python -m pytest
```

## Local setup

```bash
cp .env.example .env
python -m pip install -e '.[dev]'
pytest
```

Azure settings are optional for deterministic local development. Keep `.env`
local and never commit it.

## Limitations

The demonstration uses synthetic manifests and stored evidence only. It does
not connect to a brokerage, live market data, CI/CD, MCP, or Azure. Human
owners remain accountable for reviewing evidence and acting on the decision.
