"""AC-10: admin SLA policy versioning API (api-contracts.md, E4-S1)."""

from __future__ import annotations

from tests.conftest import auth_header


def test_AC10_admin_creates_version_2_and_version_1_unchanged(client) -> None:
    admin = auth_header(client, "admin1")
    before = client.get("/api/admin/sla-policies", params={"priority": "High"}, headers=admin)
    v1 = before.json()[0]
    resp = client.post(
        "/api/admin/sla-policies",
        json={"priority": "High", "response_minutes": 45, "resolution_minutes": 360},
        headers=admin,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["version"] == 2
    assert body["priority"] == "High"
    assert body["response_minutes"] == 45
    after = client.get("/api/admin/sla-policies", params={"priority": "High"}, headers=admin).json()
    unchanged = [row for row in after if row["version"] == 1][0]
    assert unchanged == v1


def test_AC10_list_versions_newest_first(client) -> None:
    admin = auth_header(client, "admin1")
    client.post(
        "/api/admin/sla-policies",
        json={"priority": "Low", "response_minutes": 500, "resolution_minutes": 3000},
        headers=admin,
    )
    rows = client.get(
        "/api/admin/sla-policies", params={"priority": "Low"}, headers=admin
    ).json()
    assert [r["version"] for r in rows] == [2, 1]


def test_AC10_patch_put_delete_on_published_version_are_immutable(client) -> None:
    admin = auth_header(client, "admin1")
    for method in ("patch", "put", "delete"):
        resp = getattr(client, method)("/api/admin/sla-policies/versions/1", headers=admin)
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "POLICY_VERSION_IMMUTABLE"
    rows = client.get(
        "/api/admin/sla-policies", params={"priority": "Critical"}, headers=admin
    ).json()
    assert len(rows) == 1


def test_AC10_float_value_is_rejected_with_422(client) -> None:
    admin = auth_header(client, "admin1")
    resp = client.post(
        "/api/admin/sla-policies",
        json={"priority": "High", "response_minutes": 45.5, "resolution_minutes": 360},
        headers=admin,
    )
    assert resp.status_code == 422


def test_AC10_resolution_below_response_is_rejected_with_422(client) -> None:
    admin = auth_header(client, "admin1")
    resp = client.post(
        "/api/admin/sla-policies",
        json={"priority": "High", "response_minutes": 100, "resolution_minutes": 50},
        headers=admin,
    )
    assert resp.status_code == 422


def test_AC10_agent_caller_is_forbidden(client) -> None:
    agent = auth_header(client, "agent1")
    resp = client.post(
        "/api/admin/sla-policies",
        json={"priority": "High", "response_minutes": 45, "resolution_minutes": 360},
        headers=agent,
    )
    assert resp.status_code == 403


def test_AC10_agent_cannot_mutate_a_published_version(client) -> None:
    agent = auth_header(client, "agent1")
    resp = client.patch("/api/admin/sla-policies/versions/1", headers=agent)
    assert resp.status_code == 403


def test_AC10_agent_cannot_list_policies(client) -> None:
    agent = auth_header(client, "agent1")
    resp = client.get("/api/admin/sla-policies", headers=agent)
    assert resp.status_code == 403
