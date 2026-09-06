"""Lecture du registre des paramètres (Annexe E) — `season_params`.

Un seul point de lecture pour tout le code arène : jamais de valeur de jeu
en dur ailleurs (ARENA.md §3 — "Aucune valeur de jeu en dur : tout passe
par le registre des paramètres").
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.models import SeasonParam


async def get_param(db: AsyncSession, season_id: str, name: str, *, default: Any = None) -> Any:
    row = (
        await db.execute(
            select(SeasonParam.value).where(
                SeasonParam.season_id == season_id, SeasonParam.name == name
            )
        )
    ).scalar_one_or_none()
    if row is None:
        if default is not None:
            return default
        raise KeyError(f"season_param manquant : {name} (season_id={season_id})")
    return row
