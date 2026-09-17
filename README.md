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

Stage 0 foundation: package metadata, local configuration, and test setup only.
The assurance workflow and agents are planned for later stages.

## Local setup

```bash
cp .env.example .env
python -m pip install -e '.[dev]'
pytest
```

Azure settings are optional for deterministic local development. Keep `.env`
local and never commit it.
