from __future__ import annotations

from fastapi.testclient import TestClient


def test_E6S3_cors_preflight_from_configured_frontend_origin_is_allowed(
    client: TestClient,
) -> None:
    resp = client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resp.status_code == 200
    assert resp.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_E6S3_cors_preflight_from_an_unlisted_origin_is_not_allowed(
    client: TestClient,
) -> None:
    resp = client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://evil.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert "access-control-allow-origin" not in resp.headers
