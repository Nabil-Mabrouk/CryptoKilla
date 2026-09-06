"""Provisioning d'une saison/dynastie — partagé entre le seed de dev
(`seed.py`) et les endpoints admin (`app/domain/routers.py`). Un seul
endroit qui sait « comment naît une dynastie » (dynastie + son premier
agent + capital crédité) pour ne pas dupliquer cette logique.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.models import Agent, CapitalLedger, Dynasty, Season, SeasonParam
from app.domain.arena.params import DEFAULT_SEASON_PARAMS


async def create_season(
    db: AsyncSession, *, state: str = "active", mode: str = "perpetuelle", params_overrides: dict[str, Any] | None = None
) -> Season:
    season = Season(state=state, mode=mode)
    db.add(season)
    await db.flush()

    values = dict(DEFAULT_SEASON_PARAMS)
    if params_overrides:
        values.update(params_overrides)
    for name, value in values.items():
        db.add(SeasonParam(season_id=season.id, name=name, value=value, visibility="public"))

    return season


async def create_dynasty(db: AsyncSession, *, season_id: str, name: str, model: str, color: str) -> Dynasty:
    """Crée une dynastie ET son premier agent (génération 1, capital
    crédité) — une dynastie sans agent ne peut rien faire (chapitre 27 :
    une dynastie EST représentée par ses agents vivants/morts)."""
    dynasty = Dynasty(season_id=season_id, name=name, model=model, color=color)
    db.add(dynasty)
    await db.flush()

    agent = Agent(dynasty_id=dynasty.id, generation=1, status="actif")
    db.add(agent)
    await db.flush()

    season_param = await db.get(SeasonParam, {"season_id": season_id, "name": "capital_initial"})
    capital_initial = season_param.value if season_param is not None else DEFAULT_SEASON_PARAMS["capital_initial"]
    db.add(CapitalLedger(agent_id=agent.id, event_id=None, kind="capital_initial", amount=capital_initial))

    return dynasty
