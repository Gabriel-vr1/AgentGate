"""Loopback-only reviewer UI using the Python standard library."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from agentgate.runner import execute
from agentgate.tools.policy_tools import deterministic_review_paths

CASES = {"unsafe": "unsafe_candidate", "safe": "safe_candidate", "incomplete": "incomplete_candidate"}


def review(root, case, mode):
    if case not in CASES or mode not in {"local_deterministic", "foundry"}:
        raise ValueError("Choose a controlled scenario and execution mode")
    candidate = CASES[case]
    paths = (root / "data/manifests/baseline_agent.json", root / f"data/manifests/{candidate}.json",
             root / "data/policies/release_policy.json", root / "data/policies/risk_taxonomy.json",
             root / "data/test_catalogue.json", root / f"data/test_results/{candidate}.json")
    decision, trace = execute(paths, mode)
    deterministic = deterministic_review_paths(paths[0], paths[1], paths[2], paths[4], paths[5])
    return {"scenario": case, "decision": decision.model_dump(mode="json"), "trace": trace,
            "review": deterministic.model_dump(mode="json"),
            "baseline": json.loads(paths[0].read_text()), "candidate": json.loads(paths[1].read_text()),
            "evidence": json.loads(paths[5].read_text())}


def make_handler(root):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path != "/":
                self.send(404, b"Not found", "text/plain")
                return
            self.send(200, Path(__file__).with_name("reviewer.html").read_bytes(), "text/html; charset=utf-8")

        def do_POST(self):
            # Cloud requests must originate from this loopback page.
            expected = f"http://127.0.0.1:{self.server.server_port}"
            if self.headers.get("Origin") != expected or self.headers.get("Content-Type") != "application/json":
                self.send(403, b"Forbidden origin", "text/plain")
                return
            if self.path != "/api/review":
                self.send(404, b"Not found", "text/plain")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 1024:
                    raise ValueError("Invalid request size")
                request = json.loads(self.rfile.read(length))
                result = review(root, request["scenario"], request["mode"])
                self.send(200, json.dumps(result).encode(), "application/json")
            except Exception as error:
                # Avoid returning arbitrary SDK errors or credentials to browsers.
                body = {"error": "Review failed safely. No cloud decision issued. Run local mode or inspect CLI diagnostics.",
                        "error_type": type(error).__name__}
                self.send(422, json.dumps(body).encode(), "application/json")
    return Handler


def serve(root, port=8765):
    with HTTPServer(("127.0.0.1", port), make_handler(root)) as server:
        print(f"AgentGate reviewer: http://127.0.0.1:{port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
