"""Idempotence et rejouabilité — DoD couche C1 : « l'intégralité de
l'historique est rejouable depuis les événements seuls » (chapitre 34).
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.domain.arena.agents.llm_client import ScriptedLLMClient
from app.domain.arena.engine import simulated_executor
from app.domain.arena.engine.surveillance import surveillance_tick
from app.domain.arena.models import CapitalLedger, EventRecord, MarketCandle, OrderbookSnapshot, Position
from app.domain.arena.orchestrator.hourly import run_hourly_sequence
from app.domain.arena.orchestrator.validation import validate_order


async def _seed_market(db, pair: str, price: float, n_candles: int = 60, volume: float = 10.0):
    now = datetime.now(timezone.utc)
    for i in range(n_candles):
        db.add(
            MarketCandle(
                pair=pair,
                candle_time=now - timedelta(minutes=n_candles - i),
                open=price,
                high=price,
                low=price,
                close=price,
                volume=volume,
            )
        )
    db.add(OrderbookSnapshot(pair=pair, bid=price - 1, ask=price + 1))
    await db.flush()


async def test_hourly_sequence_is_idempotent(db_session, seeded_agent):
    season, agent = seeded_agent
    await _seed_market(db_session, "BTC/EUR", 42_000)
    await _seed_market(db_session, "ETH/EUR", 2_500)

    llm_client = ScriptedLLMClient()
    ran_first = await run_hourly_sequence(db_session, season.id, ["BTC/EUR", "ETH/EUR"], llm_client)
    ran_second = await run_hourly_sequence(db_session, season.id, ["BTC/EUR", "ETH/EUR"], llm_client)

    assert ran_first is True
    assert ran_second is False  # N-C12-11 : pas rejoué dans la même heure

    allocations = (
        await db_session.execute(select(EventRecord).where(EventRecord.type == "tokens.allocation"))
    ).scalars().all()
    assert len(allocations) == 1  # une seule allocation pour l'agent, pas deux

    bulletins = (
        await db_session.execute(select(EventRecord).where(EventRecord.type == "market.bulletin"))
    ).scalars().all()
    assert len(bulletins) == 1


async def test_open_and_stop_triggered_close_matches_fill_model(db_session, seeded_agent):
    season, agent = seeded_agent
    db_session.add(CapitalLedger(agent_id=agent.id, event_id=None, kind="capital_initial", amount=10_000))
    await db_session.flush()
    await _seed_market(db_session, "BTC/EUR", 42_000)

    order = await validate_order(
        db_session,
        agent_id=agent.id,
        season_id=season.id,
        payload={
            "action": "open",
            "pair": "BTC/EUR",
            "side": "buy",
            "size": 1_000,
            "order_type": "market",
            "stop_loss": 41_000,
        },
    )
    assert order.status == "accepte"
    order = await simulated_executor.place(db_session, order)
    assert order.status == "execute"
    await db_session.commit()

    position = (
        await db_session.execute(select(Position).where(Position.agent_id == agent.id, Position.status == "ouverte"))
    ).scalar_one()

    # Bougie qui touche le stop (mèche basse sous 41000, N-C13-10).
    db_session.add(
        MarketCandle(
            pair="BTC/EUR",
            candle_time=datetime.now(timezone.utc),
            open=41_500,
            high=41_500,
            low=40_500,
            close=41_200,
            volume=10.0,
        )
    )
    await db_session.flush()

    await surveillance_tick(db_session, season.id, ["BTC/EUR"])

    await db_session.refresh(position)
    assert position.status == "fermee"
    assert position.close_reason == "stop"
    assert position.pnl < 0  # stop touché sous le prix d'entrée -> perte

    # Rejouabilité (DoD C1) : le capital final recalculé depuis le seul
    # ledger (N-C15-02 : append-only, jamais de colonne `balance` mutable)
    # correspond exactement à capital_initial + pnl_net de la position —
    # aucune double écriture, aucune écriture perdue.
    capital_rows = (
        await db_session.execute(select(CapitalLedger.amount).where(CapitalLedger.agent_id == agent.id))
    ).scalars().all()
    assert float(sum(capital_rows)) == pytest.approx(10_000 + float(position.pnl))
