"""Knowledge base article reads and writes (E5-S1, AC-09).

Articles are mutable (title, body, tags) by agents and admins; only
`source_ticket_id` is fixed once created.
"""

from __future__ import annotations

from sqlalchemy import Connection, text

from src.types.models import KbArticleRecord, KbArticleSummary


def _tags_for(conn: Connection, article_id: int) -> tuple[str, ...]:
    rows = conn.execute(
        text("SELECT tag FROM kb_article_tag WHERE article_id = :id ORDER BY tag"),
        {"id": article_id},
    ).all()
    return tuple(row[0] for row in rows)


def _replace_tags(conn: Connection, article_id: int, tags: list[str]) -> None:
    conn.execute(
        text("DELETE FROM kb_article_tag WHERE article_id = :id"), {"id": article_id}
    )
    for tag in tags:
        conn.execute(
            text(
                "INSERT INTO kb_article_tag (article_id, tag) VALUES (:article_id, :tag)"
            ),
            {"article_id": article_id, "tag": tag},
        )


def insert(
    conn: Connection,
    *,
    title: str,
    body: str,
    tags: list[str],
    source_ticket_id: str,
    created_by: str,
    created_at: str,
) -> KbArticleRecord:
    result = conn.execute(
        text(
            "INSERT INTO kb_article "
            "(title, body, source_ticket_id, created_by, created_at, updated_at) "
            "VALUES (:title, :body, :source_ticket_id, :created_by, :created_at, :created_at)"
        ),
        {
            "title": title,
            "body": body,
            "source_ticket_id": source_ticket_id,
            "created_by": created_by,
            "created_at": created_at,
        },
    )
    article_id = result.lastrowid
    assert article_id is not None
    _replace_tags(conn, int(article_id), tags)
    return KbArticleRecord(
        id=int(article_id),
        title=title,
        body=body,
        tags=tuple(tags),
        source_ticket_id=source_ticket_id,
        created_by=created_by,
        updated_at=created_at,
    )


def get_by_id(conn: Connection, article_id: int) -> KbArticleRecord | None:
    row = (
        conn.execute(text("SELECT * FROM kb_article WHERE id = :id"), {"id": article_id})
        .mappings()
        .first()
    )
    if row is None:
        return None
    return KbArticleRecord(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        tags=_tags_for(conn, article_id),
        source_ticket_id=row["source_ticket_id"],
        created_by=row["created_by"],
        updated_at=row["updated_at"],
    )


def list_articles(
    conn: Connection, *, q: str | None, tag: str | None
) -> list[KbArticleSummary]:
    sql = "SELECT DISTINCT a.id, a.title, a.updated_at FROM kb_article a"
    params: dict[str, str] = {}
    conditions = []
    if tag is not None:
        sql += " JOIN kb_article_tag t ON t.article_id = a.id"
        conditions.append("t.tag = :tag")
        params["tag"] = tag
    if q is not None:
        conditions.append("(lower(a.title) LIKE :q OR lower(a.body) LIKE :q)")
        params["q"] = f"%{q.lower()}%"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY a.id"
    rows = conn.execute(text(sql), params).mappings().all()
    return [
        KbArticleSummary(
            id=row["id"],
            title=row["title"],
            tags=_tags_for(conn, row["id"]),
            updated_at=row["updated_at"],
        )
        for row in rows
    ]


def update(
    conn: Connection,
    *,
    article_id: int,
    title: str,
    body: str,
    tags: list[str],
    updated_at: str,
) -> KbArticleRecord | None:
    result = conn.execute(
        text(
            "UPDATE kb_article SET title = :title, body = :body, updated_at = :updated_at "
            "WHERE id = :id"
        ),
        {"title": title, "body": body, "updated_at": updated_at, "id": article_id},
    )
    if result.rowcount == 0:
        return None
    _replace_tags(conn, article_id, tags)
    return get_by_id(conn, article_id)


def delete(conn: Connection, *, article_id: int) -> bool:
    result = conn.execute(
        text("DELETE FROM kb_article_tag WHERE article_id = :id"), {"id": article_id}
    )
    result = conn.execute(text("DELETE FROM kb_article WHERE id = :id"), {"id": article_id})
    return result.rowcount > 0
