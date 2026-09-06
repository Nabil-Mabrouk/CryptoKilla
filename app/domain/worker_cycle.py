"""Cycle métier du worker — couche C1 (Livre, chapitre 34).

Le châssis (`app/modules/worker/runner.py`) appelle `run_cycle` UNE fois
puis attend `WORKER_INTERVAL_SECONDS` avant le prochain appel — inadapté à
nos cadences réelles (capture ~1 min, surveillance continue, séquence
horaire, agent réactif). Décision d'architecture (plan C1, décision 6) :
`run_cycle` DEVIENT la boucle persistante — elle ne rend la main qu'à
l'arrêt (`stop_requested`). `WORKER_INTERVAL_SECONDS` n'a alors plus
d'effet pratique tant que ce fichier ne retourne pas normalement.

Le `db` fourni par le châssis (une session par appel, liée au `WorkerRun`
de ce run) n'est PAS réutilisé pour le travail de fond : chaque tâche
interne ouvre ses propres sessions via `SessionLocal` (pattern déjà
utilisé par `agents/loop.py`), pour ne jamais garder une connexion
ouverte pendant les temps d'attente.

Deux familles de tâches concurrentes (`asyncio.gather`), communiquant
UNIQUEMENT via la base (N-C11-03) :
- Les ticks (mécaniques, sans LLM) : capture marché, surveillance des
  stops/TP, déclenchement de la séquence horaire au franchissement d'heure.
- La boucle de chaque agent vivant (une par agent — un seul en C1),
  réactive, PAS rythmée par les ticks (N-C16-02).
"""

from __future__ import annotations

import asyncio

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.domain.arena.agents.llm_client import build_llm_client
from app.domain.arena.agents.loop import run_agent_loop
from app.domain.arena.capture.service import capture_tick
from app.domain.arena.engine.surveillance import surveillance_tick
from app.domain.arena.log import log
from app.domain.arena.models import Agent, Season
from app.domain.arena.orchestrator.hourly import run_hourly_sequence
from app.domain.arena.params import get_param

TICK_INTERVAL_SECONDS = 30  # capture + surveillance + check H+0
NO_SEASON_RETRY_SECONDS = 60


async def run_cycle(db: AsyncSession, stop_requested: asyncio.Event) -> None:
    settings = get_settings()

    if settings.environment == "development":
        # Dev uniquement : provisionne saison/dynastie/agent de test s'il
        # n'y en a pas déjà (idempotent). En production, une saison se crée
        # par une action délibérée (chapitre 36 — pas ce code, jamais
        # auto-provisionné en silence).
        from app.domain.arena.seed import seed_dev_season

        await seed_dev_season()

    season_id, agent_id = await _wait_for_season(stop_requested)
    if season_id is None:  # stop_requested levé avant qu'une saison existe
        return

    async with SessionLocal() as setup_db:
        pairs = await get_param(setup_db, season_id, "liste_paires", default=[])

    llm_client = build_llm_client()

    async with httpx.AsyncClient(timeout=10.0) as http_client:
        tasks = [asyncio.create_task(_tick_loop(http_client, season_id, pairs, stop_requested))]
        if agent_id is not None:
            tasks.append(
                asyncio.create_task(run_agent_loop(SessionLocal, agent_id, season_id, llm_client, stop_requested))
            )
        await asyncio.gather(*tasks, return_exceptions=True)


async def _wait_for_season(stop_requested: asyncio.Event) -> tuple[str | None, str | None]:
    """Attend qu'une saison (et, si possible, un agent) existe — un worker
    peut démarrer avant toute configuration de saison en production.

    Tolère aussi une base pas encore migrée : `docker-compose.yml` ne fait
    dépendre `backend`/`worker` que de `db: service_healthy`, pas de la fin
    du service `migrate` (comportement hérité du châssis, pas propre à ce
    module) — une course transitoire au tout premier démarrage est donc
    possible. Sans ce `try/except`, l'exception remonterait jusqu'au
    châssis (`app/modules/worker/runner.py`), qui marquerait le run
    `failed` et attendrait `WORKER_INTERVAL_SECONDS` (1h par défaut) avant
    de réessayer — bien plus lent que notre propre retry ci-dessous.
    """
    from sqlalchemy.exc import OperationalError, ProgrammingError

    while not stop_requested.is_set():
        try:
            async with SessionLocal() as db:
                season = (await db.execute(select(Season).limit(1))).scalar_one_or_none()
                if season is not None:
                    agent = (
                        await db.execute(select(Agent).where(Agent.status != "mort").limit(1))
                    ).scalar_one_or_none()
                    return season.id, (agent.id if agent else None)
        except (OperationalError, ProgrammingError) as exc:
            print(f"worker_cycle: base pas encore prête ({exc!r}) — nouvelle tentative dans {NO_SEASON_RETRY_SECONDS}s")
        try:
            await asyncio.wait_for(stop_requested.wait(), timeout=NO_SEASON_RETRY_SECONDS)
        except asyncio.TimeoutError:
            pass
    return None, None


async def _tick_loop(
    http_client: httpx.AsyncClient, season_id: str, pairs: list[str], stop_requested: asyncio.Event
) -> None:
    """Chaque étape est isolée dans son propre `try/except` : une exception
    dans l'une ne doit jamais arrêter les suivantes NI tuer cette tâche
    pour de bon — sans ça, `asyncio.gather(..., return_exceptions=True)`
    (`run_cycle`) avalerait l'exception et cette boucle s'arrêterait
    silencieusement jusqu'au redémarrage du worker (plus aucune capture,
    plus aucune surveillance des stops, jamais signalé nulle part)."""
    steps = (
        ("capture", lambda db: capture_tick(db, http_client, pairs)),
        ("surveillance", lambda db: surveillance_tick(db, season_id, pairs)),
        ("hourly", lambda db: run_hourly_sequence(db, season_id, pairs)),
    )
    while not stop_requested.is_set():
        for component, step in steps:
            try:
                async with SessionLocal() as db:
                    await step(db)
            except Exception as exc:  # noqa: BLE001 — une étape cassée ne doit jamais arrêter le tick
                print(f"worker_cycle: échec étape={component}: {exc!r}")
                try:
                    async with SessionLocal() as log_db:
                        await log(log_db, "error", component, f"Échec du tick {component}", {"error": repr(exc)})
                        await log_db.commit()
                except Exception:  # noqa: BLE001 — le logging lui-même ne doit jamais faire tomber le tick
                    pass

        try:
            await asyncio.wait_for(stop_requested.wait(), timeout=TICK_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            pass
