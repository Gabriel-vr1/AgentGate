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

Stage 2 deterministic foundation: controlled domain schemas and data, exact
manifest diffs, policy controls, stored evidence validation, and deterministic
release verdicts. Foundry agents are the next stage; workflow orchestration and
the final application are not implemented.

## Controlled demonstration

The local demonstration compares the synthetic market-research baseline with
three candidates:

- unsafe authority expansion: **BLOCK**
- safe bounded improvement: **APPROVE**
- missing assurance evidence: **CONDITIONAL**

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
