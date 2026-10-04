"""NFR-06: every request carries an X-Correlation-Id, echoed on the response."""

from __future__ import annotations

import re

from fastapi.testclient import TestClient

HEX_ID = re.compile(r"^[0-9a-f]{32}$")


def test_NFR06_response_echoes_a_valid_incoming_correlation_id(client: TestClient) -> None:
    resp = client.get("/health", headers={"X-Correlation-Id": "req-abc-123"})

    assert resp.headers["X-Correlation-Id"] == "req-abc-123"


def test_NFR06_generates_a_correlation_id_when_none_is_sent(client: TestClient) -> None:
    resp = client.get("/health")

    assert HEX_ID.match(resp.headers["X-Correlation-Id"])


def test_NFR06_unsafe_incoming_correlation_id_is_replaced(client: TestClient) -> None:
    for unsafe in ("x" * 200, "evil;rm -rf"):
        resp = client.get("/health", headers={"X-Correlation-Id": unsafe})

        assert resp.headers["X-Correlation-Id"] != unsafe
        assert HEX_ID.match(resp.headers["X-Correlation-Id"])


def test_NFR06_each_request_gets_its_own_correlation_id(client: TestClient) -> None:
    first = client.get("/health").headers["X-Correlation-Id"]
    second = client.get("/health").headers["X-Correlation-Id"]

    assert first != second


def test_NFR06_correlation_id_header_is_present_on_error_responses(client: TestClient) -> None:
    resp = client.get("/no-such-route", headers={"X-Correlation-Id": "req-404"})

    assert resp.status_code == 404
    assert resp.headers["X-Correlation-Id"] == "req-404"


def test_NFR06_correlation_id_header_is_exposed_to_the_browser(client: TestClient) -> None:
    resp = client.get("/health", headers={"Origin": "http://localhost:5173"})

    exposed = resp.headers.get("access-control-expose-headers", "").lower()
    assert "x-correlation-id" in exposed
