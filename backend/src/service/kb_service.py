"""Knowledge base orchestration: publish, search, read, edit, delete
(api-contracts.md, AC-09).
"""

from __future__ import annotations

from sqlalchemy import Engine

from src.domain.kb import validate_tags
from src.repository import kb_repository, ticket_repository
from src.types.clock import Clock
from src.types.errors import NotFoundError, SourceTicketNotResolvedError
from src.types.models import KbArticleRecord, KbArticleSummary

_PUBLISHABLE_STATUSES = {"RESOLVED", "CLOSED"}


def publish_article(
    engine: Engine,
    clock: Clock,
    *,
    source_ticket_id: str,
    title: str,
    body: str,
    tags: list[str],
    created_by: str,
) -> KbArticleRecord:
    validate_tags(tags)
    with engine.begin() as conn:
        ticket = ticket_repository.get_by_id_in_conn(conn, source_ticket_id)
        if ticket is None:
            raise NotFoundError(f"Ticket '{source_ticket_id}' not found")
        if ticket.status not in _PUBLISHABLE_STATUSES:
            raise SourceTicketNotResolvedError(
                f"Ticket '{source_ticket_id}' is not RESOLVED or CLOSED"
            )
        return kb_repository.insert(
            conn,
            title=title,
            body=body,
            tags=tags,
            source_ticket_id=source_ticket_id,
            created_by=created_by,
            created_at=clock.now().isoformat(),
        )


def list_articles(
    engine: Engine, *, q: str | None, tag: str | None
) -> list[KbArticleSummary]:
    with engine.connect() as conn:
        return kb_repository.list_articles(conn, q=q, tag=tag)


def get_article(engine: Engine, article_id: int) -> KbArticleRecord:
    with engine.connect() as conn:
        article = kb_repository.get_by_id(conn, article_id)
    if article is None:
        raise NotFoundError(f"Article '{article_id}' not found")
    return article


def update_article(
    engine: Engine,
    clock: Clock,
    *,
    article_id: int,
    title: str,
    body: str,
    tags: list[str],
) -> KbArticleRecord:
    validate_tags(tags)
    with engine.begin() as conn:
        updated = kb_repository.update(
            conn,
            article_id=article_id,
            title=title,
            body=body,
            tags=tags,
            updated_at=clock.now().isoformat(),
        )
    if updated is None:
        raise NotFoundError(f"Article '{article_id}' not found")
    return updated


def delete_article(engine: Engine, *, article_id: int) -> None:
    with engine.begin() as conn:
        deleted = kb_repository.delete(conn, article_id=article_id)
    if not deleted:
        raise NotFoundError(f"Article '{article_id}' not found")
