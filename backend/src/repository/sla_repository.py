"""The one SLA domain function that runs on every ticket read and write
(escalation_spec.md: "no scheduler"; sla-policy-evaluator, escalation-checker
skills). Evaluates the response and resolution timers, records at most one
breach SlaEvent per timer, and escalates to tier 2 at most once per ticket.

A CLOSED ticket is never written to, even by a read (escalation-checker
skill), so only the pure snapshot is computed for it.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Connection, Engine

from src.domain.escalation import tier2_slug_for
from src.domain.sla import SlaSnapshot, breach_deadline, evaluate_sla
from src.repository import sla_event_repository, sla_policy_repository, team_repository
from src.repository import ticket_repository as tickets
from src.types.models import TicketRecord

_TIMER_EVENTS = {
    "response": "BREACHED_RESPONSE",
    "resolution": "BREACHED_RESOLUTION",
}


def _parse(value: str | None) -> datetime | None:
    return None if value is None else datetime.fromisoformat(value)


def _record_breaches(
    conn: Connection, *, ticket_id: str, created_at: datetime, snapshot: SlaSnapshot, now_iso: str
) -> bool:
    """Insert one SlaEvent per timer newly found BREACHED. Returns whether any
    were recorded; `has_breach` makes a repeat call a no-op per timer.
    """
    newly_breached = False
    for timer_name, timer_snapshot in (
        ("response", snapshot.response),
        ("resolution", snapshot.resolution),
    ):
        if timer_snapshot.state != "BREACHED":
            continue
        if sla_event_repository.has_breach(conn, ticket_id, timer_name):
            continue
        deadline = breach_deadline(created_at, timer_snapshot.target_minutes)
        sla_event_repository.insert(
            conn,
            ticket_id=ticket_id,
            event=_TIMER_EVENTS[timer_name],
            timer=timer_name,
            breached_at=deadline.isoformat(),
            created_at=now_iso,
        )
        newly_breached = True
    return newly_breached


def _escalate_if_needed(
    conn: Connection, *, ticket: TicketRecord, now: datetime, now_iso: str
) -> None:
    """Move `ticket` to its tier-2 queue once, the first time any timer
    breaches (escalation_spec.md). A no-op once `ticket.escalated` is set.
    """
    if ticket.escalated:
        return
    tier2_slug = tier2_slug_for(ticket.queue.slug)
    tier2_queue_id = team_repository.get_id_by_slug(conn, tier2_slug)
    if tier2_queue_id is None:
        return
    tickets.escalate(conn, ticket_id=ticket.id, to_queue_id=tier2_queue_id, now=now)
    sla_event_repository.insert(
        conn,
        ticket_id=ticket.id,
        event="ESCALATED",
        timer=None,
        breached_at=None,
        created_at=now_iso,
    )


def evaluate_and_escalate(engine: Engine, *, ticket_id: str, now: datetime) -> SlaSnapshot | None:
    """Return the current SLA snapshot for `ticket_id`, or `None` if it does
    not exist. Recording breaches and escalating happen in the same
    transaction as the read, so a concurrent read never double-writes.
    """
    with engine.begin() as conn:
        ticket = tickets.get_by_id_in_conn(conn, ticket_id)
        if ticket is None:
            return None

        response_target, resolution_target = sla_policy_repository.get_targets(
            conn, ticket.sla_policy_version_id
        )
        created_at = _parse(ticket.created_at)
        assert created_at is not None
        snapshot = evaluate_sla(
            created_at=created_at,
            now=now,
            response_target_minutes=response_target,
            resolution_target_minutes=resolution_target,
            response_stopped_at=_parse(ticket.response_stopped_at),
            resolution_stopped_at=_parse(ticket.resolution_stopped_at),
        )

        if ticket.status == "CLOSED":
            return snapshot

        now_iso = now.isoformat()
        newly_breached = _record_breaches(
            conn, ticket_id=ticket_id, created_at=created_at, snapshot=snapshot, now_iso=now_iso
        )
        if newly_breached:
            _escalate_if_needed(conn, ticket=ticket, now=now, now_iso=now_iso)

        return snapshot
