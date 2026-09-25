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
    text(f"{number} / 5", 510, 804, width=40, size=8)


def block(top, title, body, height=105):
    rect(48, top, 499, height, PALE)
    text(title, 64, top+14, width=465, size=13, color=BLUE, bold=True)
    text(body, 64, top+40, width=465)


page(1, "Evidence Before Authority", "Technical architecture, safety controls and verified demonstration results")
text("Release assurance for changes in agent authority", 48, 144, size=22, color=BLUE, bold=True)
text("AgentGate compares a baseline and candidate synthetic agent release, identifies authority changes, checks controlled policy and assurance evidence, and returns an auditable release decision.", 48, 216, size=13)
block(304, "The release moment", "For an engineering reviewer or release owner deciding whether an agent upgrade has enough evidence to receive additional authority.")
block(425, "The problem", "An ordinary-looking upgrade can add order placement, write access or transaction authority while removing human approval. Passing stored tests does not make a policy violation acceptable.", 120)
rect(48, 569, 499, 119, BLUE)
text("CENTRAL DEMONSTRATION", 65, 584, size=10, color=white, bold=True)
text("Unsafe authority expansion: BLOCK", 65, 610, size=20, color=white, bold=True)
text("Two deterministic policy blockers prevent release approval, even when all ten selected stored assurance results pass.", 65, 648, width=462, color=white)
text("Intended impact: make authority escalation visible and require accountable remediation before release. This demonstration uses synthetic manifests and stored evidence; it performs no trading.", 48, 713, size=10)
c.showPage()

page(2, "Architecture", "Three Foundry-backed model stages, constrained by authoritative Python")
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
for i, (title, detail, model) in enumerate(nodes):
    top = 139+i*66
    rect(65, top, 465, 54, TEAL if model else PALE)
    text(title, 79, top+6, width=437, size=12, color=white if model else BLUE, bold=True)
    text(detail, 79, top+29, width=437, size=9.5, color=white if model else INK)
    if i < 7:
        c.setStrokeColor(TEAL)
        c.line(297, H-top-54, 297, H-top-64)
        c.line(294, H-top-61, 297, H-top-64)
        c.line(300, H-top-61, 297, H-top-64)
text("Teal = model reasoning. Blue-tinted = Python / application. This is a responsibility diagram; Python validates each handoff throughout the workflow.", 65, 682, width=465, size=10)
text("Microsoft Foundry project-scoped Responses calls use the existing gpt-4.1-mini deployment. These are not persistent portal-agent resources. Explicit local deterministic mode remains available.", 65, 728, width=465, size=10)
c.showPage()

page(3, "Governance and safety", "Python owns authoritative decision fields; model explanations remain advisory")
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

page(4, "Verified demonstration", "Three live Foundry cases; nine stage calls accepted on their first attempt")
rows = [("UNSAFE", "BLOCK", "11.57 s", "#a12932"), ("SAFE", "APPROVE", "8.32 s", "#087f83"), ("INCOMPLETE", "CONDITIONAL", "7.98 s", "#885600")]
for i, (scenario, verdict, duration, shade) in enumerate(rows):
    top = 140+i*74
    rect(48, top, 499, 61, PALE)
    text(scenario, 64, top+11, width=118, size=10, bold=True)
    text(verdict, 186, top+9, width=205, size=18, color=HexColor(shade), bold=True)
    text(duration+" model calls", 401, top+16, width=130, size=9)
text("Live runs: 25 September 2026, 04:55 UTC. Durations sum model requests; they are not browser latency benchmarks. All three stages ran for each case.", 48, 371, size=10)
block(427, "Unsafe authority changes", "Order-placement tool added  |  Brokerage READ to WRITE<br/>Transaction authority: USD 0 to USD 5,000<br/>Mandatory human approval removed", 113)
text("53", 60, 566, width=190, size=35, color=TEAL, bold=True)
text("automated tests passed", 60, 612, width=205, size=12)
text("13 / 13", 310, 566, width=220, size=35, color=TEAL, bold=True)
text("repository evaluation cases passed", 310, 612, width=223, size=11)
text("Evaluation = 10 labelled cases + 3 demonstrations. Six BLOCK-labelled cases reuse the unsafe manifest; these results do not establish general policy coverage or formal Foundry evaluation.", 48, 670, size=10.5)
text("Evidence: docs/evidence/live-run-summary.json and scenario trace/decision pairs. Unsafe is blocked; safe is approved; missing evidence is conditional.", 48, 730, size=10)
c.showPage()

page(5, "Evidence and reproduction", "Inspect the record, reproduce the local review and understand the limits")
text("Evidence that can be inspected", 48, 139, size=15, color=BLUE, bold=True)
text("Local structured application JSON traces record stage status, Foundry response identifiers, timing, token usage and the final decision. The reviewer can download its review and trace. These are not Azure Monitor or Application Insights traces.", 48, 168)
text(f'<link href="{URL}"><u>{URL}</u></link>', 48, 244, size=11, color=TEAL)
text(f'<link href="{URL}/blob/main/docs/verification.md"><u>Verified evidence index and detailed qualifications</u></link>', 48, 269, size=11, color=TEAL)
text("Windows / PowerShell: reproduce local mode", 48, 307, size=15, color=BLUE, bold=True)
commands = ["git clone https://github.com/Gabriel-vr1/AgentGate.git", "cd AgentGate", "py -3.12 -m venv .venv", ".venv/Scripts/python.exe -m pip install -e '.[dev,foundry]'", ".venv/Scripts/python.exe app.py serve"]
rect(48, 338, 499, 118, PALE)
for i, command in enumerate(commands):
    c.setFillColor(INK)
    c.setFont("Courier", 9)
    c.drawString(62, H-358-i*19, command)
text("Open http://127.0.0.1:8765. Choose a scenario and Run review. For live mode, use an existing permitted Foundry project, Azure CLI sign-in, project endpoint and deployment settings described in README. No resources are provisioned by the application.", 48, 474, size=10.5)
text("Limits and future work", 48, 558, size=15, color=BLUE, bold=True)
text("Synthetic fixtures and a fixed risk mapping bound coverage. Model explanations remain advisory: schema validity does not establish narrative truth, and saved safe-case prose includes unsupported test commentary. Python-owned decision fields remain authoritative.", 48, 588, size=10.5)
text("Persistent agent resources, portal telemetry, formal Foundry evaluation and fresh candidate-test execution are deferred. The reviewer is a local demonstration, without hosted authentication or production deployment. No commercial impact figures are claimed.", 48, 674, size=10.5)
text("The human release owner remains accountable for the decision and remediation.", 48, 749, size=10, color=TEAL, bold=True)
c.showPage()
c.save()

# A portable standalone diagram, using the same architecture labels as page 2.
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="1080" viewBox="0 0 960 1080">', '<rect width="960" height="1080" fill="white"/>', '<style>text{font-family:Arial,sans-serif}</style>', '<text x="60" y="55" font-size="29" fill="#103451" font-weight="bold">AgentGate | Evidence Before Authority</text>', '<text x="60" y="91" font-size="19" fill="#233b4c">Three Foundry-backed model stages constrained by Python</text>']
for i, (title, detail, model) in enumerate(nodes):
    y = 120+i*106
    color, fg = ("#087f83", "white") if model else ("#eef5f8", "#103451")
    svg += [f'<rect x="60" y="{y}" width="840" height="86" rx="10" fill="{color}"/>', f'<text x="84" y="{y+32}" font-size="24" font-weight="bold" fill="{fg}">{escape(title)}</text>', f'<text x="84" y="{y+62}" font-size="18" fill="{fg}">{escape(detail)}</text>']
    if i < 7:
        svg += [f'<path d="M480 {y+86}v18m-5-5 5 5 5-5" fill="none" stroke="#087f83" stroke-width="2"/>']
svg += ['<text x="60" y="1010" font-size="18" fill="#233b4c">Responsibility flow; Python validates each handoff throughout.</text>', '<text x="60" y="1042" font-size="18" fill="#233b4c">Model stages are not persistent portal agents. Local fallback is explicit.</text>', '</svg>']
(ROOT / "architecture-diagram.svg").write_text("\n".join(svg), encoding="utf-8")
print(OUTPUT)
