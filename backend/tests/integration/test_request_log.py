"""NFR-06: one JSON request line per HTTP request, with no request or response bodies."""

from __future__ import annotations

import io
import json

from fastapi.testclient import TestClient

from src.config.logging_setup import configure_logging


def _request_lines(stream: io.StringIO) -> list[dict[str, object]]:
    records = [json.loads(line) for line in stream.getvalue().splitlines() if line]
    return [r for r in records if r["logger"] == "helpdesk.request"]


def test_NFR06_each_request_writes_one_line_with_the_response_correlation_id(
    client: TestClient, log_stream: io.StringIO
) -> None:
    configure_logging("INFO", stream=log_stream)

    resp = client.get("/health", headers={"X-Correlation-Id": "req-log-001"})

    lines = _request_lines(log_stream)
    assert len(lines) == 1
    assert lines[0]["method"] == "GET"
    assert lines[0]["path"] == "/health"
    assert lines[0]["status"] == 200
    assert isinstance(lines[0]["duration_ms"], int)
    assert lines[0]["duration_ms"] >= 0
    assert lines[0]["correlation_id"] == resp.headers["X-Correlation-Id"] == "req-log-001"


def test_NFR06_request_line_omits_the_query_string(
    client: TestClient, log_stream: io.StringIO
) -> None:
    configure_logging("INFO", stream=log_stream)

    client.get("/health?email=jane.doe@example.test&token=abc123")

    lines = _request_lines(log_stream)
    assert lines[0]["path"] == "/health"
    assert "jane.doe@example.test" not in log_stream.getvalue()
    assert "token=abc123" not in json.dumps(_request_lines(log_stream))


def test_NFR06_request_line_never_contains_the_request_body(
    client: TestClient, log_stream: io.StringIO
) -> None:
    configure_logging("INFO", stream=log_stream)

    resp = client.post(
        "/api/auth/login", json={"username": "customer1", "password": "Hunter2-synthetic"}
    )

    assert resp.status_code == 401
    assert _request_lines(log_stream)[0]["status"] == 401
    assert "Hunter2-synthetic" not in log_stream.getvalue()


def test_NFR06_request_line_records_the_error_status(
    client: TestClient, log_stream: io.StringIO
) -> None:
    configure_logging("INFO", stream=log_stream)

    resp = client.get("/no-such-route")

    assert resp.status_code == 404
    assert _request_lines(log_stream)[0]["status"] == 404
