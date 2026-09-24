# AgentGate project rules

- Keep scope limited to synthetic agent release assurance. No real trading,
  live data, CI/CD, MCP, extra industries, Streamlit, or Azure provisioning.
- Use exactly three specialized components: Change Analyst, Assurance Planner,
  and Release Judge.
- Python is authoritative for schemas, exact diffs, policy blockers, evidence
  validation, test selection/results, and the verdict floor.
- Local deterministic mode must be labeled honestly. Foundry adapters may be
  added later without changing the handoff contracts or guardrails.
- Change Analyst explains only supplied diffs; Assurance Planner uses only the
  controlled taxonomy, policy, and catalogue; Release Judge cannot invent
  evidence or downgrade a deterministic BLOCK.
- Run the complete pytest suite and the three CLI demonstrations before a
  release commit.
- Current stage: governed local assurance workflow; Foundry integration is the
  next stage.