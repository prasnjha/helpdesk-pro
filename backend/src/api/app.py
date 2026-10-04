"""FastAPI app factory. Keeps construction testable (engine/clock are injected)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Engine

from src.api.correlation_middleware import CORRELATION_HEADER, CorrelationIdMiddleware
from src.api.error_handlers import register_error_handlers
from src.api.routers import admin, agent, auth, health, kb, tickets
from src.repository.token_store import TokenStore
from src.types.clock import Clock


def create_app(engine: Engine, clock: Clock, cors_allowed_origins: list[str]) -> FastAPI:
    app = FastAPI(title="HelpDesk Pro API")
    app.state.engine = engine
    app.state.clock = clock
    app.state.token_store = TokenStore()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_allowed_origins,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=[CORRELATION_HEADER],
    )
    # Added last so it is the outermost middleware: every HTTP response carries the id.
    app.add_middleware(CorrelationIdMiddleware)

    register_error_handlers(app)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(tickets.router)
    app.include_router(admin.router)
    app.include_router(admin.dashboard_router)
    app.include_router(kb.router)
    app.include_router(agent.router)

    return app
