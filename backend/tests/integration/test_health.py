from __future__ import annotations

from fastapi.testclient import TestClient


def test_E1S3_health_returns_200_without_token(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200


def test_E1S3_health_body_status_ok(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.json() == {"status": "ok"}
