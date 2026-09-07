from __future__ import annotations

import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base
import app.core.models  # noqa: F401 — `users`, référencée par les FK de arena/models.py (C2)
import app.domain.arena.models  # noqa: F401 — enregistre les tables sur Base.metadata

from app.domain.arena.models import Dynasty, Season, SeasonParam, Agent

DEFAULT_PARAMS = {
    "liste_paires": ["BTC/EUR", "ETH/EUR"],
    "risque_max_trade": 1.5,
    "taille_max_ordre": 5_000,
    "k_slippage": 0.002,
    "slippage_max": 0.002,
    "part_max_liquidite": 0.05,
    "frais_par_ordre": 0.0025,
    "latence_simulee": 1,
    "allocation_horaire_par_modele": 50_000,
    "plafond_solde_tokens": 10,
    "pool_plancher": 0,
    "pool_bonus_audience": 0,
}


@pytest_asyncio.fixture
async def db_session():
    # StaticPool : une connexion unique conservée pour tout le moteur — sans
    # ça, chaque nouvelle connexion sqlite ":memory:" verrait une base VIDE
    # distincte (comportement par défaut de SQLite en mémoire).
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def seeded_agent(db_session):
    """Une saison active + une dynastie + un agent + les season_params
    nécessaires aux tests — pas de capital crédité (les tests qui en ont
    besoin l'ajoutent explicitement, pour rester lisibles sur ce qu'ils
    vérifient)."""
    season = Season(state="active", mode="perpetuelle")
    db_session.add(season)
    await db_session.flush()
    for name, value in DEFAULT_PARAMS.items():
        db_session.add(SeasonParam(season_id=season.id, name=name, value=value, visibility="public"))

    dynasty = Dynasty(season_id=season.id, name="test-dynasty", model="claude", color="#FF7A45")
    db_session.add(dynasty)
    await db_session.flush()

    agent = Agent(dynasty_id=dynasty.id, generation=1, status="actif")
    db_session.add(agent)
    await db_session.flush()

    return season, agent
