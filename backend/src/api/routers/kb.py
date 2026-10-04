"""Knowledge base endpoints: publish, search, read, edit, delete (AC-09, E5-S1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Engine

from src.api.deps import get_clock, get_engine, require_role
from src.service.kb_service import delete_article as delete_article_service
from src.service.kb_service import get_article as get_article_service
from src.service.kb_service import list_articles as list_articles_service
from src.service.kb_service import publish_article as publish_article_service
from src.service.kb_service import update_article as update_article_service
from src.types.clock import Clock
from src.types.models import KbArticleRecord, KbArticleSummary, UserRecord

router = APIRouter(prefix="/api/kb/articles")


class CreateArticleRequest(BaseModel):
    source_ticket_id: str
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=5000)
    tags: list[str]


class UpdateArticleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=5000)
    tags: list[str]


class ArticleOut(BaseModel):
    id: int
    title: str
    body: str
    tags: list[str]
    source_ticket_id: str
    created_by: str
    updated_at: str


class ArticleSummaryOut(BaseModel):
    id: int
    title: str
    tags: list[str]
    updated_at: str


def _article_out(record: KbArticleRecord) -> ArticleOut:
    return ArticleOut(
        id=record.id,
        title=record.title,
        body=record.body,
        tags=list(record.tags),
        source_ticket_id=record.source_ticket_id,
        created_by=record.created_by,
        updated_at=record.updated_at,
    )


def _summary_out(record: KbArticleSummary) -> ArticleSummaryOut:
    return ArticleSummaryOut(
        id=record.id, title=record.title, tags=list(record.tags), updated_at=record.updated_at
    )


@router.post("", response_model=ArticleOut, status_code=201)
def create_article(
    payload: CreateArticleRequest,
    engine: Engine = Depends(get_engine),
    clock: Clock = Depends(get_clock),
    user: UserRecord = Depends(require_role("agent", "admin")),
) -> ArticleOut:
    article = publish_article_service(
        engine,
        clock,
        source_ticket_id=payload.source_ticket_id,
        title=payload.title,
        body=payload.body,
        tags=payload.tags,
        created_by=user.id,
    )
    return _article_out(article)


@router.get("", response_model=list[ArticleSummaryOut])
def list_articles(
    q: str | None = None,
    tag: str | None = None,
    engine: Engine = Depends(get_engine),
    user: UserRecord = Depends(require_role("customer", "agent", "admin")),
) -> list[ArticleSummaryOut]:
    return [_summary_out(a) for a in list_articles_service(engine, q=q, tag=tag)]


@router.get("/{article_id}", response_model=ArticleOut)
def get_article(
    article_id: int,
    engine: Engine = Depends(get_engine),
    user: UserRecord = Depends(require_role("customer", "agent", "admin")),
) -> ArticleOut:
    return _article_out(get_article_service(engine, article_id))


@router.put("/{article_id}", response_model=ArticleOut)
def update_article(
    article_id: int,
    payload: UpdateArticleRequest,
    engine: Engine = Depends(get_engine),
    clock: Clock = Depends(get_clock),
    user: UserRecord = Depends(require_role("agent", "admin")),
) -> ArticleOut:
    article = update_article_service(
        engine,
        clock,
        article_id=article_id,
        title=payload.title,
        body=payload.body,
        tags=payload.tags,
    )
    return _article_out(article)


@router.delete("/{article_id}", status_code=204)
def delete_article(
    article_id: int,
    engine: Engine = Depends(get_engine),
    user: UserRecord = Depends(require_role("agent", "admin")),
) -> None:
    delete_article_service(engine, article_id=article_id)
