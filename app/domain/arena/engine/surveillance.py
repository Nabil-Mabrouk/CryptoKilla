"""Surveillance continue des stops/TP (N-C13-02) — indépendante de l'état
cognitif de l'agent : tourne même en veille, même orchestrateur down.

Règle de la mèche (N-C13-10) : un stop/TP est réputé touché dès qu'une
bougie 1 min touche son niveau (high/low), pas seulement à la clôture.

Un fill déclenché ici n'a pas d'`Order` d'origine (personne ne l'a soumis)
— `_settle_close` accepte `order_id=None` pour ce cas précisément
(`Fill.order_id` est nullable dans le modèle pour cette raison).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.capture.service import latest_candles, latest_orderbook
from app.domain.arena.engine import fill_model
from app.domain.arena.engine.simulated_executor import _settle_close
from app.domain.arena.models import Position
from app.domain.arena.params import get_param


async def surveillance_tick(db: AsyncSession, season_id: str, pairs: list[str]) -> None:
    frais_par_ordre = await get_param(db, season_id, "frais_par_ordre", default=0.0025)
    k_slippage = await get_param(db, season_id, "k_slippage", default=0.002)
    slippage_max = await get_param(db, season_id, "slippage_max", default=0.002)

    for pair in pairs:
        candles, stale, _age = await latest_candles(db, pair, limit=60)
        if stale or not candles:
            continue  # panne de flux : pas de nouvelle bougie à vérifier ce tick
        last = candles[-1]

        open_positions = (
            await db.execute(select(Position).where(Position.pair == pair, Position.status == "ouverte"))
        ).scalars().all()
        if not open_positions:
            continue

        book = await latest_orderbook(db, pair)
        if book is None:
            continue
        ref = (book.bid + book.ask) / 2
        hs = fill_model.half_spread(book.bid, book.ask, ref)
        volume_1h = sum(c.volume for c in candles) * ref

        for position in open_positions:
            await _check_position(
                db, season_id, position, last, hs, volume_1h, frais_par_ordre, k_slippage, slippage_max
            )
    await db.commit()


async def _check_position(
    db: AsyncSession,
    season_id: str,
    position: Position,
    candle,
    hs: float,
    volume_1h: float,
    frais_par_ordre: float,
    k_slippage: float,
    slippage_max: float,
) -> None:
    close_side = fill_model.closing_side(position.side)
    stop_level = float(position.stop_loss)
    stop_touched = (
        candle.low <= stop_level if position.side == "buy" else candle.high >= stop_level
    )
    take_profit = position.take_profit
    tp_touched = take_profit is not None and (
        candle.high >= float(take_profit) if position.side == "buy" else candle.low <= float(take_profit)
    )
    if not stop_touched and not tp_touched:
        return

    if stop_touched:
        slip = fill_model.slippage(float(position.size), volume_1h, k_slippage, slippage_max)
        fill_price = fill_model.stop_fill(stop_level, hs, slip, close_side)
        close_reason = "stop"
    else:
        fill_price = fill_model.take_profit_fill(float(take_profit))
        slip = 0.0
        close_reason = "take_profit"

    await _settle_close(
        db,
        season_id=season_id,
        agent_id=position.agent_id,
        position=position,
        fill_price=fill_price,
        slip=slip,
        frais_par_ordre=frais_par_ordre,
        close_reason=close_reason,
        order_id=None,
    )
