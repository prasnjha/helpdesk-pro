"""AC-09: knowledge base publish and CRUD API (api-contracts.md, E5-S1)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import auth_header

VALID_PAYLOAD = {
    "title": "Invoice charged twice",
    "description": "I was billed twice for the same invoice.",
    "category": "Billing",
    "priority": "High",
}


def _create_ticket(client: TestClient) -> str:
    headers = auth_header(client, "customer1")
    resp = client.post("/api/tickets", json=VALID_PAYLOAD, headers=headers)
    ticket_id: str = resp.json()["id"]
    return ticket_id


def _resolve_ticket(client: TestClient, ticket_id: str) -> None:
    agent = auth_header(client, "agent1")
    client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"to_status": "IN_PROGRESS", "version": 1},
        headers=agent,
    )
    client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"to_status": "RESOLVED", "version": 2},
        headers=agent,
    )


def test_AC09_F017_agent_publishes_article_for_resolved_ticket_returns_201(
    client: TestClient,
) -> None:
    ticket_id = _create_ticket(client)
    _resolve_ticket(client, ticket_id)
    agent = auth_header(client, "agent1")

    resp = client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "How to fix duplicate invoices",
            "body": "Check the billing ledger for duplicate charge rows.",
            "tags": ["billing", "invoice"],
        },
        headers=agent,
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["source_ticket_id"] == ticket_id
    assert body["title"] == "How to fix duplicate invoices"
    assert body["tags"] == ["billing", "invoice"]


def test_AC09_open_source_ticket_returns_409_source_ticket_not_resolved(
    client: TestClient,
) -> None:
    ticket_id = _create_ticket(client)
    agent = auth_header(client, "agent1")

    resp = client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Draft",
            "body": "Draft body",
            "tags": ["billing"],
        },
        headers=agent,
    )

    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "SOURCE_TICKET_NOT_RESOLVED"


def test_AC09_F018_customer_post_put_delete_return_403_and_table_unchanged(
    client: TestClient, engine
) -> None:
    ticket_id = _create_ticket(client)
    _resolve_ticket(client, ticket_id)
    agent = auth_header(client, "agent1")
    customer = auth_header(client, "customer1")

    created = client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Original title",
            "body": "Original body",
            "tags": ["billing"],
        },
        headers=agent,
    ).json()
    article_id = created["id"]

    post_resp = client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Hijack",
            "body": "Hijack body",
            "tags": ["billing"],
        },
        headers=customer,
    )
    put_resp = client.put(
        f"/api/kb/articles/{article_id}",
        json={"title": "Hijacked", "body": "Hijacked body", "tags": ["billing"]},
        headers=customer,
    )
    delete_resp = client.delete(f"/api/kb/articles/{article_id}", headers=customer)

    assert post_resp.status_code == 403
    assert put_resp.status_code == 403
    assert delete_resp.status_code == 403

    with engine.connect() as conn:
        from sqlalchemy import text

        count = conn.execute(text("SELECT COUNT(*) FROM kb_article")).scalar_one()
        unchanged = conn.execute(
            text("SELECT title, body FROM kb_article WHERE id = :id"), {"id": article_id}
        ).first()
    assert count == 1
    assert unchanged[0] == "Original title"
    assert unchanged[1] == "Original body"


def test_AC09_customer_search_by_title_or_body_substring(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    _resolve_ticket(client, ticket_id)
    agent = auth_header(client, "agent1")
    client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Reset your password",
            "body": "Go to settings and reset it.",
            "tags": ["account"],
        },
        headers=agent,
    )
    client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Unrelated",
            "body": "Nothing to see here.",
            "tags": ["account"],
        },
        headers=agent,
    )

    customer = auth_header(client, "customer1")
    resp = client.get("/api/kb/articles", params={"q": "password"}, headers=customer)

    assert resp.status_code == 200
    titles = [row["title"] for row in resp.json()]
    assert titles == ["Reset your password"]


def test_AC09_filter_by_tag_returns_only_matching_articles(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    _resolve_ticket(client, ticket_id)
    agent = auth_header(client, "agent1")
    client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Billing article",
            "body": "About billing.",
            "tags": ["billing"],
        },
        headers=agent,
    )
    client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Account article",
            "body": "About accounts.",
            "tags": ["account"],
        },
        headers=agent,
    )

    resp = client.get("/api/kb/articles", params={"tag": "account"}, headers=agent)

    assert resp.status_code == 200
    titles = [row["title"] for row in resp.json()]
    assert titles == ["Account article"]


def test_AC09_get_article_returns_source_ticket_id_for_customer(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    _resolve_ticket(client, ticket_id)
    agent = auth_header(client, "agent1")
    created = client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Topic",
            "body": "Body",
            "tags": ["billing"],
        },
        headers=agent,
    ).json()

    customer = auth_header(client, "customer1")
    resp = client.get(f"/api/kb/articles/{created['id']}", headers=customer)

    assert resp.status_code == 200
    assert resp.json()["source_ticket_id"] == ticket_id


def test_AC09_unknown_article_returns_404(client: TestClient) -> None:
    agent = auth_header(client, "agent1")
    resp = client.get("/api/kb/articles/999999", headers=agent)
    assert resp.status_code == 404


def test_AC09_update_cannot_change_source_ticket_id(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    _resolve_ticket(client, ticket_id)
    agent = auth_header(client, "agent1")
    created = client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Topic",
            "body": "Body",
            "tags": ["billing"],
        },
        headers=agent,
    ).json()

    resp = client.put(
        f"/api/kb/articles/{created['id']}",
        json={
            "title": "New title",
            "body": "New body",
            "tags": ["billing"],
            "source_ticket_id": "HD-999999",
        },
        headers=agent,
    )

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_AC09_agent_updates_article_tags_are_saved(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    _resolve_ticket(client, ticket_id)
    agent = auth_header(client, "agent1")
    created = client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Topic",
            "body": "Body",
            "tags": ["billing"],
        },
        headers=agent,
    ).json()

    resp = client.put(
        f"/api/kb/articles/{created['id']}",
        json={"title": "New title", "body": "New body", "tags": ["billing", "refund"]},
        headers=agent,
    )

    assert resp.status_code == 200
    assert resp.json()["tags"] == ["billing", "refund"]


def test_AC09_admin_deletes_article_returns_204(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    _resolve_ticket(client, ticket_id)
    agent = auth_header(client, "agent1")
    admin = auth_header(client, "admin1")
    created = client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Topic",
            "body": "Body",
            "tags": ["billing"],
        },
        headers=agent,
    ).json()

    resp = client.delete(f"/api/kb/articles/{created['id']}", headers=admin)

    assert resp.status_code == 204
    assert client.get(f"/api/kb/articles/{created['id']}", headers=admin).status_code == 404


def test_AC09_unknown_source_ticket_returns_404(client: TestClient) -> None:
    agent = auth_header(client, "agent1")

    resp = client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": "HD-999999",
            "title": "Topic",
            "body": "Body",
            "tags": ["billing"],
        },
        headers=agent,
    )

    assert resp.status_code == 404


def test_AC09_update_unknown_article_returns_404(client: TestClient) -> None:
    agent = auth_header(client, "agent1")

    resp = client.put(
        "/api/kb/articles/999999",
        json={"title": "Topic", "body": "Body", "tags": ["billing"]},
        headers=agent,
    )

    assert resp.status_code == 404


def test_AC09_delete_unknown_article_returns_404(client: TestClient) -> None:
    agent = auth_header(client, "agent1")

    resp = client.delete("/api/kb/articles/999999", headers=agent)

    assert resp.status_code == 404


def test_AC09_invalid_tags_return_422(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    _resolve_ticket(client, ticket_id)
    agent = auth_header(client, "agent1")

    resp = client.post(
        "/api/kb/articles",
        json={
            "source_ticket_id": ticket_id,
            "title": "Topic",
            "body": "Body",
            "tags": ["Billing"],
        },
        headers=agent,
    )

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
