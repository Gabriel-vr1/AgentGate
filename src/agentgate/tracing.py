"""Portable application trace evidence. No Azure Monitor export is implied."""
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4


class RunTrace:
    def __init__(self, mode):
        self.document = {"trace_id": uuid4().hex, "started_at": datetime.now(timezone.utc).isoformat(),
                         "execution_mode": mode, "trace_backend": "local_json", "status": "RUNNING", "spans": []}

    def record(self, event, started):
        self.document["spans"].append({**event, "duration_ms": round((perf_counter() - started) * 1000, 2)})

    def finish(self, decision):
        self.document.update(status="COMPLETED", decision=decision.model_dump(mode="json"))

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.document, indent=2) + "\n", encoding="utf-8")
