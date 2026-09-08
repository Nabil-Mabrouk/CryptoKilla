"""Journal opérationnel — un seul point d'écriture dans `arena_logs`
(diagnostics admin, distinct de `arena_events`, voir `models.ArenaLog`).
"""

from __future__ import annotations

import traceback
from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.models import ArenaLog

Level = Literal["info", "warning", "error"]


async def log(db: AsyncSession, level: Level, component: str, message: str, details: dict[str, Any] | None = None) -> None:
    db.add(ArenaLog(level=level, component=component, message=message, details=details))
    await db.flush()


def error_details(exc: BaseException) -> dict[str, Any]:
    """`repr(exc)` seul est trompeur pour les exceptions "enveloppe" (ex.
    `anthropic.APIConnectionError('Connection error.')`, dont le vrai
    responsable — DNS, TLS, timeout, refus de connexion — voyage dans
    `__cause__`/`__context__`, jamais dans le message affiché). Capture
    aussi la traceback complète (bornée) pour ne pas devoir redéployer
    juste pour voir OÙ l'exception a été levée."""
    cause = exc.__cause__ or exc.__context__
    return {
        "error": repr(exc),
        "cause": repr(cause) if cause is not None else None,
        "traceback": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[-4000:],
    }
