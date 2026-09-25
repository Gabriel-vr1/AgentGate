# AgentGate

**Evidence before authority.** AgentGate compares two synthetic AI-agent releases,
checks the candidate against controlled policy and stored assurance evidence,
and returns **APPROVE**, **CONDITIONAL**, or **BLOCK**.

Microsoft Foundry powers three narrowly scoped stages: **Change Analyst**,
**Assurance Planner**, and **Release Judge**. Python owns exact diffs, risk
categories, policy findings, test selection, evidence validation, remediation,
and the verdict floor. An LLM cannot downgrade a deterministic BLOCK.

## Submission status

- Verified live on 25 September 2026: all three stages used the existing
  `gpt-4.1-mini` deployment in Foundry project `agentgate`, Spain Central.
- Unsafe authority expansion returned **BLOCK**, with no repair required.
- [Saved live trace](docs/evidence/unsafe-foundry-trace.json) includes three
  service response IDs, token usage, durations, model explanations, and the final decision.
- [Saved decision](docs/evidence/unsafe-foundry-decision.json) and
  [evaluation results](docs/evidence/evaluation-results.json) are included.
- 53 tests and all 13 controlled evaluation/demo cases pass.
- The compact reviewer UI is implemented and HTTP-tested. Browser visual QA
  could not run because the automation session exposed no available browser.

## Run the reviewer

From this repository in Windows PowerShell, using the existing Python 3.12 environment:

```powershell
.venv/Scripts/python.exe -m pip install -e '.[dev,foundry]'
.venv/Scripts/python.exe app.py serve
```

Open **http://127.0.0.1:8765**. Choose a scenario and select **Run review**.
The page shows baseline/candidate releases, authority changes, policy findings,
selected assurance tests, stored evidence, verdict, remediation and stage explanations.
Use **Download review + trace** to export the full result. Stop the server with Ctrl+C.
Use `--port 8766` if the default port is occupied.

Local mode requires no Azure credentials or cloud SDKs; install `.[dev]` for an
offline-only setup. Local execution is explicitly labeled `local_deterministic`.

## Connect the existing Foundry project

Set these non-secret values in the terminal **before starting the server**:

```powershell
$env:AZURE_AI_PROJECT_ENDPOINT='https://agentgate-foundry-gvr0710.services.ai.azure.com/api/projects/agentgate'
$env:AZURE_AI_MODEL_DEPLOYMENT_NAME='gpt-4.1-mini'
.venv/Scripts/python.exe app.py serve
```

Alternatively, copy `.env.example` to `.env`. Keep `.env` untracked. The adapter
uses `AzureCliCredential` and the existing Azure CLI login; use `az login` only
if your session needs refreshing. No API keys are needed. The project endpoint
is checked before authentication. No Azure resources or hosted agents are created.

Select **Microsoft Foundry ? live model** in the page, or run:

```powershell
.venv/Scripts/python.exe app.py run unsafe --mode foundry --save out/unsafe-decision.json --trace out/unsafe-trace.json
```

This makes three bounded model requests in the normal path. Each stage permits
at most one structured-output repair. SDK retries are disabled, requests have a
45-second timeout, and output is bounded. Authentication/transport failure or
invalid output after repair fails the cloud run without issuing a cloud decision.
Run local mode explicitly to obtain the deterministic fallback decision.

## Demonstrations and verification

```powershell
.venv/Scripts/python.exe app.py list
.venv/Scripts/python.exe app.py run unsafe
.venv/Scripts/python.exe app.py run safe
.venv/Scripts/python.exe app.py run incomplete
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m agentgate.evaluation
```

| Scenario | Expected verdict | Reason |
| --- | --- | --- |
| Unsafe authority expansion | BLOCK | Execution/write authority and financial limits without human approval |
| Safe bounded improvement | APPROVE | No blocking change under the controlled policy |
| Missing assurance evidence | CONDITIONAL | Required evidence is missing or not passing |

`python app.py run all` runs the three local cases together. The evaluation
command checks verdicts plus required subsets of expected controls and tests
across both JSONL suites. It returns nonzero on failure. Tests mock cloud calls;
normal test/evaluation runs do not call Azure.

## Architecture and evidence

See [architecture](docs/architecture.md), the [demo script](docs/demo_script.md),
and [verification record](docs/verification.md).

The integration uses the official [Azure AI Projects SDK and project-scoped
Responses client](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python).
The optional SDK dependency is pinned to the version verified here.

Tracing is a **local JSON application trace**, visible in the UI and saveable via
`--trace`. It is not Azure Monitor, Application Insights, OpenTelemetry export,
or proof of visibility in the Foundry portal. Requests use `store=False`.
Credentials, headers and raw SDK exception messages are not written to traces.

## Boundaries

This is a governed synthetic demonstration, not a general production release
gate. Test results are stored fixtures, not newly executed trading-agent tests.
Even a PASS fixture cannot override policy blockers. Model explanations are
advisory and may contain errors; their factual correctness is not guaranteed by
schema validation. Authoritative fields are constructed and checked in Python.
The Release Judge recommendation must equal the Python floor in this version.

Only the unsafe scenario has been verified live; all three scenario
contracts are exercised with mocked cloud responses. The UI is a single-user,
loopback-only standard-library server, not a hosted service. There is no real
trading, live market data, CI/CD, MCP, extra industry, or resource provisioning.
Human reviewers remain accountable for any release action.
