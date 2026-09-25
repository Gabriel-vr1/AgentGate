# AgentGate reproduction guide

Public source: https://github.com/Gabriel-vr1/AgentGate

## Windows PowerShell / Python 3.12

```powershell
git clone https://github.com/Gabriel-vr1/AgentGate.git
cd AgentGate
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -e '.[dev,foundry]'
.venv/Scripts/python.exe app.py serve
```

Open http://127.0.0.1:8765. Select a scenario, Local deterministic and Run review.
Expected results: unsafe BLOCK, safe APPROVE, incomplete CONDITIONAL. The server
uses loopback; this is not a hosted deployment.

For Microsoft Foundry live, authenticate Azure CLI privately and configure
`AZURE_AI_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME` for an existing
permitted project/deployment before starting the server. Follow README and
`.env.example`. No resources are created. Never commit .env or credentials.
Cloud failure stops review; choose local explicitly for an offline demo.

```powershell
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m agentgate.evaluation
.venv/Scripts/python.exe app.py run all
```

Evidence: https://github.com/Gabriel-vr1/AgentGate/blob/main/docs/verification.md .
Saved live inference is not formal Foundry evaluation or portal telemetry.

Rebuild the PDF with `docs/build_submission_pdf.py` after installing `reportlab`
in an authoring environment. ReportLab is document tooling, not an application
dependency or requirement for running AgentGate.
