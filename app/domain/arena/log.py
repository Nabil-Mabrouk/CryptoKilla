"""Journal opérationnel — un seul point d'écriture dans `arena_logs`
(diagnostics admin, distinct de `arena_events`, voir `models.ArenaLog`).
"""

from __future__ import annotations

from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.models import ArenaLog

Level = Literal["info", "warning", "error"]


async def log(db: AsyncSession, level: Level, component: str, message: str, details: dict[str, Any] | None = None) -> None:
    db.add(ArenaLog(level=level, component=component, message=message, details=details))
    await db.flush()
