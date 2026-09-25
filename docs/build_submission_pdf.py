"""Rebuild the submission PDF: python -m pip install reportlab; python docs/build_submission_pdf.py.

ReportLab is document-authoring tooling, not an application dependency.
"""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "AgentGate_Technical_Architecture_and_Evidence.pdf"
BLUE, TEAL, INK = map(HexColor, ("#103451", "#087f83", "#233b4c"))
PALE = HexColor("#eef5f8")
W, H = 595, 842
URL = "https://github.com/Gabriel-vr1/AgentGate"
c = canvas.Canvas(str(OUTPUT), pagesize=(W, H), invariant=1)
c.setTitle("AgentGate | Technical Architecture and Evidence")
c.setAuthor("AgentGate")


def text(value, x, top, width=499, size=11, color=INK, bold=False):
    style = ParagraphStyle("body", fontName="Helvetica-Bold" if bold else "Helvetica",
                           fontSize=size, leading=size * 1.38, textColor=color)
    p = Paragraph(value, style)
    _, height = p.wrap(width, H)
    p.drawOn(c, x, H-top-height)
    return height


def rect(x, top, width, height, color, radius=8):
    c.setFillColor(color)
    c.roundRect(x, H-top-height, width, height, radius, stroke=0, fill=1)


def page(number, title, subtitle):
    rect(0, 0, W, 115, BLUE, 0)
    text("AGENTGATE  /  EVIDENCE BEFORE AUTHORITY", 48, 25, size=10, color=white, bold=True)
    text(title, 48, 49, size=24, color=white, bold=True)
    text(subtitle, 48, 88, size=10, color=white)
    c.setStrokeColor(HexColor("#d5e1e8"))
    c.line(48, 47, 547, 47)
    text("Synthetic release assurance  |  Submission evidence: 25 September 2026", 48, 804, size=8)
    text(f"{number} / 6", 510, 804, width=40, size=8)


def block(top, title, body, height=105):
    rect(48, top, 499, height, PALE)
    text(title, 64, top+14, width=465, size=13, color=BLUE, bold=True)
    text(body, 64, top+40, width=465)


page(1, "Solution Design", "CURRENTLY IMPLEMENTED | Evidence Before Authority")
text("Business Problem", 48, 139, size=16, color=BLUE, bold=True)
text("An ordinary-looking agent upgrade can silently gain order placement, write access or transaction authority while removing human approval. AgentGate compares releases and requires policy and assurance evidence before authority is approved.", 48, 170, size=11.5)
block(254, "Intended Users", "Engineering reviewers and accountable release owners assessing a baseline-to-candidate agent change. A local reviewer interface and CLI expose decisions, evidence and required remediation.", 112)
block(382, "Tools and Grounding Data", "Controlled JSON manifests, policies, risk taxonomy, test catalogue and stored assurance evidence ground the workflow. Python computes the exact deterministic manifest diff and owns authoritative decision fields.", 120)
block(518, "Why Multi Agent", "Three specialized responsibilities separate change explanation, assurance planning and release judgment. This makes handoffs inspectable; strict Python validation, rather than agent agreement, establishes decision authority.", 120)
rect(48, 658, 499, 105, BLUE)
text("UNSAFE AUTHORITY EXPANSION: BLOCK", 65, 674, width=465, size=16, color=white, bold=True)
text("Two hard policy blockers stop approval even when ten selected stored results pass. Synthetic demonstration only: no trading or measured commercial impact is claimed.", 65, 710, width=465, color=white)
c.showPage()

page(2, "Agent Architecture", "CURRENTLY IMPLEMENTED prototype and clearly separated future services")
nodes = [
    ("Reviewer input", "Fixed scenario, baseline, candidate and execution mode", False),
    ("Python validation + exact manifest diff", "Strict schemas and confirmed field-level changes", False),
    ("1  Change Analyst", "Explains only the supplied deterministic diff", True),
    ("2  Assurance Planner", "Explains controlled risks, policy and selected assurance", True),
    ("Deterministic policy + assurance engine", "Checks blockers, stored evidence and the verdict floor", False),
    ("3  Release Judge", "Structured recommendation must match the Python floor", True),
    ("Non-downgrade verdict guard", "Validate references and reject conflicting model verdicts", False),
    ("Auditable decision", "APPROVE / CONDITIONAL / BLOCK + remediation + trace", False),
]
text("Specialised Agents", 48, 133, size=14, color=BLUE, bold=True)
text("Three Foundry-backed model stages; project-scoped Responses calls, not persistent portal-agent resources. Teal marks model reasoning.", 48, 157, size=10)
text("End to End Workflow", 48, 194, size=14, color=BLUE, bold=True)
c.setStrokeColor(TEAL)
c.roundRect(48, H-652, 499, 430, 8, stroke=1, fill=0)
text("IMPLEMENTED PROTOTYPE BOUNDARY", 62, 230, size=9, color=TEAL, bold=True)
for i, (title, detail, model) in enumerate(nodes):
    top = 252+i*48
    rect(62, top, 471, 40, TEAL if model else PALE)
    text(title, 74, top+4, width=445, size=10.5, color=white if model else BLUE, bold=True)
    text(detail, 74, top+22, width=445, size=8.8, color=white if model else INK)
    if i < 7:
        c.setStrokeColor(TEAL)
        c.line(297, H-top-40, 297, H-top-47)
        c.line(294, H-top-44, 297, H-top-47)
        c.line(300, H-top-44, 297, H-top-47)
text("Python validates every handoff. Responsibility flow, not an exhaustive call graph.", 62, 634, width=471, size=8)
c.setStrokeColor(BLUE)
c.setDash(4, 3)
c.roundRect(48, H-776, 499, 108, 8, stroke=1, fill=0)
c.setDash()
text("PLANNED PRODUCTION SERVICES - NOT IMPLEMENTED", 62, 678, width=471, size=10, color=BLUE, bold=True)
text("Authenticated service + enterprise identity/RBAC; managed Foundry agents if appropriate; OpenTelemetry/Foundry trace export to Application Insights; formal evaluators; controlled CI/CD approval; audit and retention services.", 62, 704, width=471, size=10)
c.showPage()

page(3, "Governance and Reliability", "CURRENTLY IMPLEMENTED | Model explanations remain advisory")
items = [
    ("Exact comparison", "Python validates manifests and computes the exact baseline-to-candidate diff. Model prose cannot add an authority change."),
    ("Controlled evidence", "A bounded taxonomy, policy and test catalogue determine selected tests. Stored results are validated, not freshly executed candidate-agent tests."),
    ("Structured handoffs", "Strict Pydantic contracts and reference checks constrain changes, plans and decisions. Each stage permits at most one structured-output repair."),
    ("Deterministic blockers", "Python owns blockers, conditions, test selection and remediation. The model verdict must equal the deterministic floor in this implementation."),
    ("Safe failure", "Unavailable Foundry calls, invalid output or invalid references stop the cloud review. Local mode is an explicit choice, never a silent replacement."),
    ("Human accountability", "The reviewer inspects the evidence and required remediation. AgentGate issues an assurance decision; it does not deploy a release or place trades."),
]
for i, (title, body) in enumerate(items):
    top = 139+i*87
    text(f"0{i+1}", 48, top, width=32, size=15, color=TEAL, bold=True)
    text(title, 92, top, width=455, size=13, color=BLUE, bold=True)
    text(body, 92, top+23, width=455, size=10.5)
rect(48, 688, 499, 76, BLUE)
text("Model output cannot downgrade validated policy blockers.", 65, 704, width=465, size=16, color=white, bold=True)
c.showPage()

page(4, "Prototype Evidence", "CURRENTLY IMPLEMENTED | Three live cases; nine first-attempt stage calls")
rows = [("UNSAFE", "BLOCK", "11.57 s", "#a12932"), ("SAFE", "APPROVE", "8.32 s", "#087f83"), ("INCOMPLETE", "CONDITIONAL", "7.98 s", "#885600")]
for i, (scenario, verdict, duration, shade) in enumerate(rows):
    top = 140+i*74
    rect(48, top, 499, 61, PALE)
    text(scenario, 64, top+11, width=118, size=10, bold=True)
    text(verdict, 186, top+9, width=205, size=18, color=HexColor(shade), bold=True)
    text(duration+" model calls", 401, top+16, width=130, size=9)
text("Live runs: 25 September 2026, 04:55 UTC. Durations sum model requests; they are not browser latency benchmarks. All three stages ran for each case.", 48, 371, size=10)
block(427, "Unsafe authority changes", "Order-placement tool added  |  Brokerage READ to WRITE<br/>Transaction authority: USD 0 to USD 5,000<br/>Mandatory human approval removed", 113)
text("Evaluation Strategy", 48, 552, size=15, color=BLUE, bold=True)
text("53", 60, 582, width=190, size=35, color=TEAL, bold=True)
text("automated tests passed", 60, 627, width=205, size=12)
text("13 / 13", 310, 582, width=220, size=35, color=TEAL, bold=True)
text("repository evaluation cases passed", 310, 627, width=223, size=11)
text("13/13 repository cases = 10 labelled cases + 3 demonstrations. Checks cover verdicts and expected control/test subsets. Six BLOCK labels reuse the unsafe manifest; this is not general coverage or formal Foundry evaluation.", 48, 670, size=10.5)
text("Evidence: docs/evidence/live-run-summary.json and scenario trace/decision pairs. Unsafe is blocked; safe is approved; missing evidence is conditional.", 48, 730, size=10)
c.showPage()

page(5, "Observability Strategy", "CURRENTLY IMPLEMENTED versus PRODUCTION-READINESS PLAN")
block(139, "CURRENTLY IMPLEMENTED", "Structured local application traces contain stage status, Foundry response IDs, timing, token usage and the final decision. The reviewer downloads decisions, evidence and trace JSON. Trace IDs connect the displayed review to its saved record.", 139)
block(296, "PRODUCTION-READINESS PLAN - NOT IMPLEMENTED", "Export OpenTelemetry/Foundry traces to Application Insights. Monitor latency, token use, validation repairs, failure rates, tool success, verdict distribution and policy-blocker frequency. Define alert thresholds and ownership before deployment.", 140)
text("Limitations", 48, 458, size=16, color=BLUE, bold=True)
text("Current traces are local JSON, not Azure Monitor or Application Insights. There are no persistent managed agents or formal Foundry evaluation jobs. Tool success is a planned operational metric; this prototype consumes stored test results and does not execute candidate-agent tools.", 48, 490, size=11)
text("Model explanations remain advisory and can contain unsupported claims: saved safe-case prose mentions tests Python did not select. Strict schemas and resolvable references do not prove narrative truth. Python-owned decision fields remain authoritative.", 48, 590, size=11)
text("Fixed policies and repeated synthetic manifests limit evaluation coverage. The reviewer is a local demonstration without hosted identity, enterprise audit retention or production approval infrastructure. No real trading or commercial impact metrics are claimed.", 48, 689, size=10.5)
c.showPage()

page(6, "Production-Readiness Plan", "PLANNED ONLY | No production services have been provisioned or verified")
text("Deployment and Continuous Improvement", 48, 136, size=16, color=BLUE, bold=True)
text("Deploy the reviewer behind an authenticated service endpoint. Add enterprise identity, role-based access, evidence retention, audit logging and human release approval. Migrate reasoning stages to persistent managed Foundry agents only if operationally appropriate; preserve deterministic non-downgrade controls.", 48, 170, size=10.5)
text("Evaluation Strategy - planned release gate", 48, 266, size=13, color=BLUE, bold=True)
text("Use formal Foundry evaluators for groundedness, task adherence, tool usage and response quality. Add representative regression cases whenever policies, tools, models or prompts change. Run evaluations before release and integrate AgentGate into a controlled CI/CD approval step with accountable human sign-off.", 48, 295, size=10.5)
text("Improvement loop: review traces and failures, add regression cases, revise the controlled policy or implementation, evaluate, then seek approval. Model-quality scores must never override deterministic blockers.", 48, 388, size=10.5)
text("Reproduce the implemented prototype", 48, 461, size=14, color=BLUE, bold=True)
commands = ["git clone https://github.com/Gabriel-vr1/AgentGate.git", "cd AgentGate", "py -3.12 -m venv .venv", ".venv/Scripts/python.exe -m pip install -e '.[dev,foundry]'", ".venv/Scripts/python.exe app.py serve"]
rect(48, 490, 499, 118, PALE)
for i, command in enumerate(commands):
    c.setFillColor(INK)
    c.setFont("Courier", 9)
    c.drawString(62, H-510-i*19, command)
text("Open http://127.0.0.1:8765. For live mode, use Azure CLI sign-in and an existing authorized project endpoint and model deployment configured as described in README. Explicit local deterministic mode remains available.", 48, 625, size=10.5)
text(f'<link href="{URL}"><u>{URL}</u></link>', 48, 697, size=11, color=TEAL)
text(f'<link href="{URL}/blob/main/docs/verification.md"><u>Evidence index, response IDs, timings and qualifications</u></link>', 48, 725, size=10.5, color=TEAL)
text("Planned services are roadmap items, not prototype capabilities or verified integrations.", 48, 759, size=9, color=BLUE, bold=True)
c.showPage()
c.save()

# A portable standalone diagram, using the same architecture labels as page 2.
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="1330" viewBox="0 0 960 1330">', '<rect width="960" height="1330" fill="white"/>', '<style>text{font-family:Arial,sans-serif}</style>', '<text x="60" y="55" font-size="29" fill="#103451" font-weight="bold">AgentGate | Evidence Before Authority</text>', '<text x="60" y="91" font-size="19" fill="#233b4c">Three Foundry-backed model stages constrained by Python</text>']
svg += ['<rect x="40" y="109" width="880" height="935" rx="10" fill="none" stroke="#087f83" stroke-width="2"/>', '<text x="60" y="141" font-size="18" fill="#087f83" font-weight="bold">IMPLEMENTED PROTOTYPE BOUNDARY</text>']
for i, (title, detail, model) in enumerate(nodes):
    y = 158+i*106
    color, fg = ("#087f83", "white") if model else ("#eef5f8", "#103451")
    svg += [f'<rect x="60" y="{y}" width="840" height="86" rx="10" fill="{color}"/>', f'<text x="84" y="{y+32}" font-size="24" font-weight="bold" fill="{fg}">{escape(title)}</text>', f'<text x="84" y="{y+62}" font-size="18" fill="{fg}">{escape(detail)}</text>']
    if i < 7:
        svg += [f'<path d="M480 {y+86}v18m-5-5 5 5 5-5" fill="none" stroke="#087f83" stroke-width="2"/>']
svg += ['<text x="60" y="1020" font-size="17" fill="#233b4c">Python validates every handoff. Model stages are not persistent agents.</text>', '<rect x="40" y="1063" width="880" height="237" rx="10" fill="none" stroke="#103451" stroke-width="2" stroke-dasharray="8 6"/>', '<text x="60" y="1100" font-size="21" fill="#103451" font-weight="bold">PLANNED PRODUCTION SERVICES - NOT IMPLEMENTED</text>', '<text x="60" y="1140" font-size="18" fill="#233b4c">Authenticated endpoint + enterprise identity / RBAC + human approval</text>', '<text x="60" y="1176" font-size="18" fill="#233b4c">Managed Foundry agents if appropriate; formal Foundry evaluators</text>', '<text x="60" y="1212" font-size="18" fill="#233b4c">OpenTelemetry / Foundry traces to Application Insights; audit / retention</text>', '<text x="60" y="1248" font-size="18" fill="#233b4c">Controlled CI/CD gate + regression evaluations before release</text>', '<text x="60" y="1282" font-size="18" fill="#087f83">Preserve deterministic non-downgrade controls in every deployment.</text>', '</svg>']
(ROOT / "architecture-diagram.svg").write_text("\n".join(svg), encoding="utf-8")
print(OUTPUT)
