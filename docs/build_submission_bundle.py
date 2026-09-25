"""Package the committed submission documents; run from any working directory."""
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DEST = ROOT / "submission"
FILES = (
    "AgentGate_Technical_Architecture_and_Evidence.pdf",
    "architecture-diagram.svg",
    "demo_script.md",
    "recording_shot_list.md",
    "submission_form_copy.md",
    "final-verification.md",
    "limitations.md",
    "reproduction-guide.md",
    "submission-status.md",
)


def link(match):
    label, target = match.groups()
    if "://" in target or target.startswith("#") or target in FILES:
        return match.group(0)
    return f"[{label}](https://github.com/Gabriel-vr1/AgentGate/blob/main/docs/{target})"


DEST.mkdir(exist_ok=True)
for name in FILES:
    source, target = DOCS / name, DEST / name
    if source.suffix == ".md":
        target.write_text(re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link,
                                 source.read_text(encoding="utf-8")), encoding="utf-8")
    else:
        shutil.copyfile(source, target)

archive = ROOT / "AgentGate_Submission_Package.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
    for name in FILES:
        bundle.write(DEST / name, f"submission/{name}")
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    assert set(bundle.namelist()) == {f"submission/{name}" for name in FILES}
print(f"Verified {len(FILES)} documents: {archive}")
