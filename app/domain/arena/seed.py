"""Seed de développement — UNE saison, UNE dynastie, UN agent.

Pas un fixture de production : réutilise `provisioning.py` (même chemin
que la création admin d'une vraie saison) avec les valeurs par défaut de
`params.DEFAULT_SEASON_PARAMS` (Annexe E, illustratives — voir sa
docstring). N'agit qu'en dev (`ENVIRONMENT=development`, garde posée par
l'appelant, `worker_cycle.py`).

Usage : `python -m app.domain.arena.seed` (idempotent — ne recrée rien si
une saison existe déjà).
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.database import SessionLocal
from app.domain.arena.models import Agent, Season
from app.domain.arena.provisioning import create_dynasty, create_season


async def seed_dev_season(dynasty_name: str = "claude-nord", model: str = "claude") -> str:
    """Crée saison + dynastie + agent s'ils n'existent pas déjà. Retourne
    l'`agent_id` (existant ou créé)."""
    async with SessionLocal() as db:
        season = (await db.execute(select(Season).limit(1))).scalar_one_or_none()
        if season is not None:
            agent = (
                await db.execute(select(Agent).where(Agent.status != "mort").limit(1))
            ).scalar_one_or_none()
            if agent is not None:
                return agent.id
        else:
            season = await create_season(db)

        dynasty = await create_dynasty(db, season_id=season.id, name=dynasty_name, model=model, color="#FF7A45")
        await db.commit()

        agent = (
            await db.execute(select(Agent).where(Agent.dynasty_id == dynasty.id).limit(1))
        ).scalar_one()
        return agent.id


if __name__ == "__main__":
    agent_id = asyncio.run(seed_dev_season())
    print(f"Seed OK — agent_id={agent_id}")
