import json
from http.client import HTTPConnection
from http.server import HTTPServer
from threading import Thread

import pytest

from agentgate.evaluation import evaluate
from agentgate.reviewer import make_handler, review
from tests.integration.test_local_workflow import ROOT


@pytest.mark.parametrize("case,verdict", [("unsafe", "BLOCK"), ("safe", "APPROVE"), ("incomplete", "CONDITIONAL")])
def test_reviewer_exposes_complete_evidence(case, verdict):
    result = review(ROOT, case, "local_deterministic")
    assert result["decision"]["verdict"] == verdict
    assert result["baseline"]["release_id"] == result["decision"]["baseline_release_id"]
    assert result["evidence"]["release_id"] == result["candidate"]["release_id"]
    assert result["trace"]["status"] == "COMPLETED"


def test_all_evaluation_expectations():
    results = evaluate(ROOT)
    assert len(results) == 13
    assert all(result["passed"] for result in results), results


def test_http_review_and_cross_origin_protection():
    server = HTTPServer(("127.0.0.1", 0), make_handler(ROOT))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    try:
        connection.request("GET", "/")
        response = connection.getresponse()
        assert response.status == 200
        assert b"Authority changes" in response.read()
        payload = json.dumps({"scenario": "unsafe", "mode": "local_deterministic"})
        connection.request("POST", "/api/review", payload, {"Content-Type": "application/json", "Origin": "https://evil.invalid"})
        response = connection.getresponse()
        assert response.status == 403
        response.read()
        connection.request("POST", "/api/review", payload, {"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{server.server_port}"})
        response = connection.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["decision"]["verdict"] == "BLOCK"
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
