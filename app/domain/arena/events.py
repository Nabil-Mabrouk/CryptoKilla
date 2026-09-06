"""Émission d'événements (Livre, Annexe B — schémas de messages).

`emit_event` est le SEUL point d'écriture dans `arena_events` : chaque
émission doit précéder tout effet observable qu'elle documente
(N-C12-11 — idempotence de la séquence horaire ; N-C11-02 — event-sourcing).

13 types (Annexe B.1, AMEND-14 : `no_trade.logged` est le 13e). C1 n'émet
que ceux nécessaires à sa DoD ; les autres (`chat.reaction`, `agent.death`,
`agent.birth`, `no_trade.logged`) existent dans l'énumération pour rester
conforme au schéma du Livre, mais aucun code de cette passe ne les produit
(mort/mémoire/réactions = hors scope C1, chat public multi-agents = C2).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.models import EventRecord

EventKind = Literal[
    "chat.message",
    "chat.reaction",
    "order.request",
    "order.rejected",
    "trade.opened",
    "trade.closed",
    "market.bulletin",
    "tokens.allocation",
    "agent.death",
    "agent.birth",
    "season.event",
    "inbox.recap",
    "no_trade.logged",  # AMEND-14, 13e type — non émis en C1 (voir plan)
]

# AMEND-13 : recipient non-null uniquement pour ces 3 types privés.
PRIVATE_TYPES = frozenset({"order.rejected", "tokens.allocation", "inbox.recap"})


async def emit_event(
    db: AsyncSession,
    *,
    season_id: str,
    kind: EventKind,
    sender: str,
    payload: dict[str, Any],
    recipient: str | None = None,
) -> EventRecord:
    """Écrit un événement dans `arena_events` et le retourne (id/timestamp
    assignés). N'effectue AUCUN commit — appelant responsable de la
    transaction, pour pouvoir grouper émission + effet dans un seul commit
    atomique (N-C12-11 : un crash entre les deux ne doit jamais laisser un
    effet sans son événement, ni l'inverse)."""
    if recipient is not None and kind not in PRIVATE_TYPES:
        raise ValueError(f"{kind} ne prend pas de recipient (AMEND-13, types privés : {sorted(PRIVATE_TYPES)})")

    record = EventRecord(
        type=kind,
        timestamp=datetime.now(timezone.utc),
        season_id=season_id,
        sender=sender,
        recipient=recipient,
        payload=payload,
    )
    db.add(record)
    await db.flush()
    return record
