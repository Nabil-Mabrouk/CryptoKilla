"""Séquence horaire H+0 — 7 étapes strictement ordonnées (N-C12-02),
idempotentes (N-C12-11). Rôles Comptable (étapes 1-4) / Arbitre (étape 5) /
Horloger (étapes 6-7) du Livre — un seul processus les exécute (décision 6
du plan), pas un rôle par processus.

C1 (un seul agent, décision de portée du plan) — étapes dégénérées mais
structurellement complètes, prêtes pour C2 sans reprise :
- 1 (gel fenêtre) et 2 (citations) : no-op, pas de chat multi-agents en C1.
- 3 (pool) : no-op, `pool_plancher`/`pool_bonus_audience` = 0 en seed dev —
  financer un pool n'a de sens qu'à plusieurs agents.
- 4 (allocations) : RÉEL — verse `allocation_horaire_par_modele` à chaque
  agent vivant.
- 5 (cycle de vie) : no-op, mort/renaissance hors DoD C1.
- 6 (bulletin) : RÉEL — publie `market.bulletin`.
- 7 (classement) : no-op ici — recalculé à la demande par
  `/api/arena/status`, pas de table de classement persistée en C1.

Idempotence (N-C12-11) : avant tout effet, vérifie qu'aucun
`market.bulletin` n'a déjà été émis pour l'heure courante — un crash
interrompant la séquence ne rejoue jamais une allocation déjà versée
(chaque étape écrit son événement avant tout effet, dans la même
transaction que l'appelant committera).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.capture.service import latest_candles
from app.domain.arena.events import emit_event
from app.domain.arena.models import Agent, Dynasty, EventRecord, TokenLedger
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


async def run_hourly_sequence(db: AsyncSession, season_id: str, pairs: list[str]) -> bool:
    """Exécute la séquence si l'heure courante n'a pas déjà été traitée.
    Retourne `True` si elle a effectivement tourné."""
    hour = current_hour_boundary()
    if await _already_ran_this_hour(db, season_id, hour):
        return False

    # Étapes 1-3 : no-op en C1 (voir docstring).
    await _step4_allocations(db, season_id)
    # Étape 5 : no-op en C1.
    await _step6_bulletin(db, season_id, pairs)
    # Étape 7 : no-op en C1 (classement calculé à la demande).

    await db.commit()
    return True


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


async def _step4_allocations(db: AsyncSession, season_id: str) -> None:
    """N-C12-12 : respecte le plafond de thésaurisation et retient en
    priorité un découvert de cycle précédent avant de créditer le reste."""
    base_amount = await get_param(db, season_id, "allocation_horaire_par_modele", default=0)
    plafond_multiple = await get_param(db, season_id, "plafond_solde_tokens", default=10)
    plafond = base_amount * plafond_multiple

    for agent in await _living_agents(db, season_id):
        balance = await _agent_token_balance(db, agent.id)
        event = await emit_event(
            db,
            season_id=season_id,
            kind="tokens.allocation",
            sender="orchestrator",
            recipient=agent.id,
            payload={"base_amount": base_amount, "pool_amount": 0, "new_balance": min(balance + base_amount, plafond)},
        )
        credited = base_amount
        if balance < 0:
            # Découvert retenu en priorité (R-21/N-C12-12) — le solde
            # négatif absorbe une partie de l'allocation avant le reste.
            decouvert = min(base_amount, -balance)
            db.add(TokenLedger(agent_id=agent.id, event_id=event.id, kind="decouvert", amount=decouvert))
            credited -= decouvert
        if balance + credited > plafond:
            credited = max(plafond - balance, 0)
        if credited:
            db.add(
                TokenLedger(agent_id=agent.id, event_id=event.id, kind="allocation_base", amount=credited)
            )


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
