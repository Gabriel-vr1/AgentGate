# AgentGate

**Evidence before authority.** AgentGate compares two synthetic AI-agent releases,
checks the candidate against controlled policy and stored assurance evidence,
and returns **APPROVE**, **CONDITIONAL**, or **BLOCK**.

Microsoft Foundry powers three narrowly scoped stages: **Change Analyst**,
**Assurance Planner**, and **Release Judge**. Python owns exact diffs, risk
categories, policy findings, test selection, evidence validation, remediation,
and the verdict floor. An LLM cannot downgrade a deterministic BLOCK.

## Submission status

All three scenarios were verified live on 25 September 2026 against the existing
`gpt-4.1-mini` deployment in project `agentgate`, Spain Central. All nine stage
calls passed validation on the first attempt.

| Live scenario | Verdict | Saved trace | Decision |
| --- | --- | --- | --- |
| Unsafe authority expansion | BLOCK | [Trace](docs/evidence/unsafe-foundry-trace.json) | [Decision](docs/evidence/unsafe-foundry-decision.json) |
| Safe bounded improvement | APPROVE | [Trace](docs/evidence/safe-foundry-trace.json) | [Decision](docs/evidence/safe-foundry-decision.json) |
| Missing assurance evidence | CONDITIONAL | [Trace](docs/evidence/incomplete-foundry-trace.json) | [Decision](docs/evidence/incomplete-foundry-decision.json) |

**Implementation type:** three Foundry-backed model stages called sequentially
by Python, not persistent Foundry agent resources. Traces are local JSON;
evaluations are local Python runs. No Application Insights or Foundry evaluation
job is claimed.

53 tests and all 13 labelled evaluation/demo cases pass. A fresh clone installs
in a new Python 3.12 environment, starts the reviewer, and returns all three
expected local verdicts over HTTP. See [verification](docs/verification.md),
[submission summary](docs/submission-summary.md), and the honest
[blueprint audit](docs/blueprint-audit.md). The original blueprint is partially
fulfilled; portal resources/telemetry/evaluation remain deferred.

## Run the reviewer

Prerequisites: Windows PowerShell, Git, and Python 3.12 (`py -3.12`). Azure CLI
and an authorized existing Foundry project/model are needed only for live mode.
From a clean checkout:

```powershell
git clone https://github.com/Gabriel-vr1/AgentGate.git
cd AgentGate
py -3.12 -m venv .venv
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

Select **Microsoft Foundry live** in the page, or run:

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
[verification record](docs/verification.md), [blueprint audit](docs/blueprint-audit.md),
and [limitations](docs/limitations.md).

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

All three scenarios have been verified live and with mocked cloud responses. The UI is a single-user,
loopback-only standard-library server, not a hosted service. There is no real
trading, live market data, CI/CD, MCP, extra industry, or resource provisioning.
Human reviewers remain accountable for any release action.

The UI has HTTP and JavaScript syntax checks but no automated browser visual QA
in this session. Model prose can mention tests that Python did not select;
use the selected-test table and decision fields as authoritative.

## Reproduce the three live evidence files

After setting the two environment variables above (or copying `.env.example`
to the ignored `.env`), run:

```powershell
.venv/Scripts/python.exe app.py run unsafe --mode foundry --save out/unsafe-decision.json --trace out/unsafe-trace.json
.venv/Scripts/python.exe app.py run safe --mode foundry --save out/safe-decision.json --trace out/safe-trace.json
.venv/Scripts/python.exe app.py run incomplete --mode foundry --save out/incomplete-decision.json --trace out/incomplete-trace.json
```

A successful live run reports `Execution mode: foundry`. On failure, no cloud
decision is issued; use `--mode local_deterministic` explicitly for fallback.
The recorded evidence is a historical run, not a guarantee of future service availability.

## Submission package

- [Technical architecture and evidence PDF](docs/AgentGate_Technical_Architecture_and_Evidence.pdf)
- [Standalone architecture diagram](docs/architecture-diagram.svg)
- [Final blueprint status](docs/submission-status.md)
- [Recording shot list](docs/recording_shot_list.md) and [spoken script](docs/demo_script.md)
- [Ready-to-paste submission form](docs/submission_form_copy.md)
- [Reproduction guide](docs/reproduction-guide.md)

The generated `submission/` folder and `AgentGate_Submission_Package.zip` are
local release artifacts and are ignored by Git. Source documents and the PDF
are committed. Rebuild the PDF using `docs/build_submission_pdf.py` with optional
ReportLab authoring tooling; no application dependencies were added.

Rebuild the local bundle with `.venv/Scripts/python.exe docs/build_submission_bundle.py`.
