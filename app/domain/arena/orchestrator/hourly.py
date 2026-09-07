"""Séquence horaire H+0 — 7 étapes strictement ordonnées (N-C12-02),
idempotentes (N-C12-11). Rôles Comptable (étapes 1-4) / Arbitre (étape 5) /
Horloger (étapes 6-7) du Livre — un seul processus les exécute (décision 6
du plan), pas un rôle par processus.

C2 :
- 1 (gel fenêtre) : RÉEL — la borne d'heure courante EST le gel (requête
  par timestamp, aucun état à écrire séparément).
- 2 (citations) : no-op ici — déjà réglé en continu par `_settle_close`
  (décision 6/8 du plan) au moment de la clôture, pas en batch horaire.
- 3 (pool) : RÉEL — `economy.classify_pending_messages` puis
  `economy.compute_hourly_pool`.
- 4 (allocations) : RÉEL — verse `allocation_horaire_par_modele` +
  `pool_amount` à chaque agent vivant.
- 5 (cycle de vie) : RÉEL — `lifecycle.process_rebirths`.
- 6 (bulletin) : RÉEL — publie `market.bulletin`.
- 7 (classement) : no-op ici — recalculé à la demande par
  `/api/arena/status`, pas de table de classement persistée.

Idempotence (N-C12-11) : avant tout effet, vérifie qu'aucun
`market.bulletin` n'a déjà été émis pour l'heure courante — un crash
interrompant la séquence ne rejoue jamais une allocation déjà versée
(chaque étape écrit son événement avant tout effet, dans la même
transaction que l'appelant committera).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.agents.llm_client import LLMClient
from app.domain.arena.capture.service import latest_candles
from app.domain.arena.events import emit_event
from app.domain.arena.models import Agent, Dynasty, EventRecord, TokenLedger
from app.domain.arena.orchestrator import economy, lifecycle
from app.domain.arena.params import get_param


def current_hour_boundary(now: datetime | None = None) -> datetime:
    now = now or datetime.now(timezone.utc)
    return now.replace(minute=0, second=0, microsecond=0)


async def _already_ran_this_hour(db: AsyncSession, season_id: str, hour: datetime) -> bool:
    existing = (
        await db.execute(
            select(EventRecord.id).where(
                EventRecord.season_id == season_id,
                EventRecord.type == "market.bulletin",
                EventRecord.timestamp >= hour,
            )
        )
    ).first()
    return existing is not None


async def run_hourly_sequence(db: AsyncSession, season_id: str, pairs: list[str], llm_client: LLMClient) -> bool:
    """Exécute la séquence si l'heure courante n'a pas déjà été traitée.
    Retourne `True` si elle a effectivement tourné."""
    hour = current_hour_boundary()
    if await _already_ran_this_hour(db, season_id, hour):
        return False

    # Étape 1 : gel de fenêtre — la fenêtre écoulée est simplement [hour-1h, hour).
    window_start = hour - timedelta(hours=1)
    # Étape 2 : no-op ici, déjà réglé en continu (voir docstring).
    pool_amounts = await _step3_pool(db, season_id, llm_client, window_start, hour)
    await _step4_allocations(db, season_id, pool_amounts)
    await lifecycle.process_rebirths(db, season_id)
    await _step6_bulletin(db, season_id, pairs)
    # Étape 7 : no-op en C1 (classement calculé à la demande).

    await db.commit()
    return True


async def _step3_pool(
    db: AsyncSession, season_id: str, llm_client: LLMClient, window_start: datetime, window_end: datetime
) -> dict[str, float]:
    await economy.classify_pending_messages(db, llm_client, season_id)
    return await economy.compute_hourly_pool(db, season_id, window_start, window_end)


async def _living_agents(db: AsyncSession, season_id: str) -> list[Agent]:
    return list(
        (
            await db.execute(
                select(Agent)
                .join(Dynasty, Agent.dynasty_id == Dynasty.id)
                .where(Dynasty.season_id == season_id, Agent.status != "mort")
            )
        ).scalars()
    )


async def _agent_token_balance(db: AsyncSession, agent_id: str) -> float:
    rows = (
        await db.execute(select(TokenLedger.amount).where(TokenLedger.agent_id == agent_id))
    ).scalars().all()
    return float(sum(rows))


async def _step4_allocations(db: AsyncSession, season_id: str, pool_amounts: dict[str, float]) -> None:
    """N-C12-12 : respecte le plafond de thésaurisation et retient en
    priorité un découvert de cycle précédent avant de créditer le reste.
    Ne concerne QUE les agents déjà vivants avant le gel (le nouveau-né de
    l'étape 5 reçoit sa propre allocation initiale, N-C12-13)."""
    base_amount = await get_param(db, season_id, "allocation_horaire_par_modele", default=0)
    plafond_multiple = await get_param(db, season_id, "plafond_solde_tokens", default=10)
    plafond = base_amount * plafond_multiple

    for agent in await _living_agents(db, season_id):
        pool_amount = pool_amounts.get(agent.id, 0.0)
        gross = base_amount + pool_amount
        balance = await _agent_token_balance(db, agent.id)
        event = await emit_event(
            db,
            season_id=season_id,
            kind="tokens.allocation",
            sender="orchestrator",
            recipient=agent.id,
            payload={"base_amount": base_amount, "pool_amount": pool_amount, "new_balance": min(balance + gross, plafond)},
        )
        credited = gross
        if balance < 0:
            # Découvert retenu en priorité (R-21/N-C12-12) — le solde
            # négatif absorbe une partie de l'allocation avant le reste.
            decouvert = min(gross, -balance)
            db.add(TokenLedger(agent_id=agent.id, event_id=event.id, kind="decouvert", amount=decouvert))
            credited -= decouvert
        if balance + credited > plafond:
            credited = max(plafond - balance, 0)
        if credited:
            base_share = credited * (base_amount / gross) if gross else 0
            pool_share = credited - base_share
            if base_share:
                db.add(TokenLedger(agent_id=agent.id, event_id=event.id, kind="allocation_base", amount=base_share))
            if pool_share:
                db.add(TokenLedger(agent_id=agent.id, event_id=event.id, kind="allocation_pool", amount=pool_share))


async def _step6_bulletin(db: AsyncSession, season_id: str, pairs: list[str]) -> None:
    """N-C14-08 : contenu exact et exhaustif par paire, rien d'autre."""
    pair_stats = []
    for pair in pairs:
        candles, stale, _age = await latest_candles(db, pair, limit=1440)
        if not candles:
            continue
        last_price = candles[-1].close
        change_1h = _pct_change(candles, minutes=60)
        change_24h = _pct_change(candles, minutes=1440)
        volume_1h = sum(c.volume for c in candles[-60:])
        pair_stats.append(
            {
                "pair": pair,
                "last_price": last_price,
                "change_1h": change_1h,
                "change_24h": change_24h,
                "volume_1h": volume_1h,
                "stale": stale,
            }
        )
    await emit_event(
        db,
        season_id=season_id,
        kind="market.bulletin",
        sender="orchestrator",
        payload={"pairs": pair_stats},
    )


def _pct_change(candles: list, minutes: int) -> float | None:
    if len(candles) < 2:
        return None
    reference = candles[-min(minutes, len(candles))]
    latest = candles[-1]
    if reference.close == 0:
        return None
    return (latest.close - reference.close) / reference.close * 100
