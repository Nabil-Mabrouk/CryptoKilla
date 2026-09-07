"""SimulatedExecutor — les 6 méthodes du moteur d'exécution (N-C13-01).

Reçoit des `Order` déjà VALIDÉS par le pipeline de l'orchestrateur
(`orchestrator/validation.py`, statut `accepte`) — ce module ne revalide
que ce qui peut avoir changé depuis (liquidité, ch.13.3/N-C13-11 : double
garde, la 2e ici, au moment du fill réel après la latence simulée).

`ref`/`half_spread`/`volume_1h` viennent de la capture (`capture/service.py`)
— jamais recalculés depuis une source différente, pour que le même prix de
référence serve à la validation ET au fill (cohérence chapitre 13).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.capture.service import latest_candles, latest_orderbook
from app.domain.arena.engine import fill_model
from app.domain.arena.events import emit_event
from app.domain.arena.models import Agent, CapitalLedger, Citation, Fill, Order, Position
from app.domain.arena.orchestrator import lifecycle
from app.domain.arena.params import get_param


class LiquidityRejected(Exception):
    """Rejet tardif E-LIQUIDITY au moment du fill (N-C12-16/N-C13-11) —
    distinct d'un rejet à la validation : l'ordre avait été `accepte`."""


async def _reference_price(db: AsyncSession, pair: str) -> tuple[float, float, float]:
    """`(ref, half_spread, volume_1h)` — panne de flux si aucune donnée."""
    book = await latest_orderbook(db, pair)
    candles, stale, _age = await latest_candles(db, pair, limit=60)
    if book is None or not candles:
        raise RuntimeError(f"Pas de données marché pour {pair} — flux en panne (N-C14-04)")
    ref = (book.bid + book.ask) / 2
    hs = fill_model.half_spread(book.bid, book.ask, ref)
    volume_1h_base = sum(c.volume for c in candles[-60:])
    volume_1h = volume_1h_base * ref
    return ref, hs, volume_1h


async def place(db: AsyncSession, order: Order) -> Order:
    """Exécute un ordre `accepte` — `open` ou `close` (les `modify` n'ont
    pas de fill, traités entièrement par la validation, N-C12-14)."""
    latence = await get_param(db, order.season_id, "latence_simulee", default=1)
    ref, hs, volume_1h = await _reference_price(db, order.pair)
    part_max_liquidite = await get_param(db, order.season_id, "part_max_liquidite", default=0.05)
    frais_par_ordre = await get_param(db, order.season_id, "frais_par_ordre", default=0.0025)

    closing_position: Position | None = None
    if order.action == "close":
        closing_position = await db.get(Position, order.position_id)
        assert closing_position is not None  # garanti par la validation (E-POSITION-UNKNOWN)
        size = float(closing_position.size)
    else:
        size = float(order.size)

    if not fill_model.check_liquidity(size, volume_1h, part_max_liquidite):
        order.status = "rejete"
        order.rejected_code = "E-LIQUIDITY"
        await emit_event(
            db,
            season_id=order.season_id,
            kind="order.rejected",
            sender="orchestrator",
            recipient=order.agent_id,
            payload={
                "order_id": order.id,
                "error_code": "E-LIQUIDITY",
                "detail": "Liquidité insuffisante au moment du fill (garde tardive, N-C13-11).",
            },
        )
        return order

    slip = fill_model.slippage(size, volume_1h,
                                await get_param(db, order.season_id, "k_slippage", default=0.002),
                                await get_param(db, order.season_id, "slippage_max", default=0.002))

    if order.action == "open":
        fill_price = fill_model.market_fill(ref, hs, slip, order.side)
        position = Position(
            agent_id=order.agent_id,
            pair=order.pair,
            side=order.side,
            size=order.size,
            stop_loss=order.stop_loss,
            take_profit=order.take_profit,
            status="ouverte",
        )
        db.add(position)
        await db.flush()
        order.position_id = position.id
        order.status = "execute"
        fees = fill_model.fees(size, frais_par_ordre)
        db.add(Fill(order_id=order.id, position_id=position.id, fill_price=fill_price, fees=fees, slippage=slip))
        db.add(CapitalLedger(agent_id=order.agent_id, event_id=None, kind="frais", amount=-fees))

        payload = {
            "position_id": position.id,
            "agent_id": order.agent_id,
            "pair": order.pair,
            "side": order.side,
            "size": size,
            "fill_price": fill_price,
            "fees": fees,
            "slippage": slip,
            "decision_summary": order.decision_summary,
        }
        if order.declared_risk_pct is not None:
            payload["declared_risk_pct"] = float(order.declared_risk_pct)
            payload["risk_calculated_pct"] = float(order.risk_calculated_pct) if order.risk_calculated_pct is not None else None
        await emit_event(db, season_id=order.season_id, kind="trade.opened", sender=order.agent_id, payload=payload)

    elif order.action == "close":
        position = closing_position
        assert position is not None
        close_side = fill_model.closing_side(position.side)
        fill_price = fill_model.market_fill(ref, hs, slip, close_side)
        await _settle_close(
            db,
            season_id=order.season_id,
            agent_id=order.agent_id,
            position=position,
            fill_price=fill_price,
            slip=slip,
            frais_par_ordre=frais_par_ordre,
            close_reason="agent_close",
            order_id=order.id,
        )
        order.status = "execute"

    return order


async def _settle_close(
    db: AsyncSession,
    *,
    season_id: str,
    agent_id: str,
    position: Position,
    fill_price: float,
    slip: float,
    frais_par_ordre: float,
    close_reason: str,
    order_id: str | None = None,
) -> None:
    fills = (
        await db.execute(select(Fill).where(Fill.position_id == position.id).order_by(Fill.executed_at))
    ).scalars().all()
    opening_fill = fills[0]

    result = fill_model.pnl_net(
        taille_ouverture=float(position.size),
        fill_entree=float(opening_fill.fill_price),
        fill_sortie=fill_price,
        frais_par_ordre=frais_par_ordre,
        side=position.side,
    )

    position.status = "fermee"
    position.close_reason = close_reason
    position.pnl = result["pnl_net"]
    position.closed_at = datetime.now(timezone.utc)

    db.add(
        Fill(
            order_id=order_id,
            position_id=position.id,
            fill_price=fill_price,
            fees=result["frais_sortie"],
            slippage=slip,
        )
    )
    # N-C15-02 : le capital est un ledger append-only, pas une colonne
    # mutable — pnl_brut et frais de sortie y sont versés séparément
    # (frais d'ouverture déjà versés dans `place()`), leur somme donnant
    # exactement `pnl_net` (Annexe F) sans double comptage.
    db.add(CapitalLedger(agent_id=agent_id, event_id=None, kind="pnl_realise", amount=result["pnl_brut"]))
    db.add(CapitalLedger(agent_id=agent_id, event_id=None, kind="frais", amount=-result["frais_sortie"]))

    # N-C06-06 : réglées à la clôture GAGNANTE du trade citant, dans la
    # fenêtre en cours de clôture (Citation.order_id référence l'ordre
    # d'OUVERTURE, seul porteur de `cites[]` — décision 8 du plan).
    if opening_fill.order_id is not None:
        pending_citations = (
            await db.execute(select(Citation).where(Citation.order_id == opening_fill.order_id, Citation.status == "en_attente"))
        ).scalars().all()
        settled_status = "creditee" if result["pnl_net"] > 0 else "non_creditee"
        for citation in pending_citations:
            citation.status = settled_status

    await emit_event(
        db,
        season_id=season_id,
        kind="trade.closed",
        sender=agent_id,
        payload={
            "position_id": position.id,
            "agent_id": agent_id,
            "side": position.side,
            "size": float(position.size),
            "close_reason": close_reason,
            "fill_price": fill_price,
            "fees": result["frais_sortie"],
            "slippage": slip,
            "pnl": result["pnl_net"],
        },
    )

    # Décision 6 du plan : le capital ne change JAMAIS ailleurs que dans
    # `_settle_close` (frais d'ouverture mis à part, jamais suffisants
    # seuls pour atteindre le seuil de mort) — seul point de déclenchement
    # possible pour le constat de mort en continu (N-C05-03).
    agent = await db.get(Agent, agent_id)
    assert agent is not None
    await lifecycle.check_death(db, agent)


async def modify(db: AsyncSession, position_id: str, stop_loss: float | None, take_profit: float | None) -> Position:
    position = await db.get(Position, position_id)
    assert position is not None
    if stop_loss is not None:
        position.stop_loss = stop_loss
    if take_profit is not None:
        position.take_profit = take_profit
    return position


async def cancel(db: AsyncSession, order_id: str) -> Order:
    order = await db.get(Order, order_id)
    assert order is not None
    order.status = "annule"
    return order


async def get_positions(db: AsyncSession, agent_id: str) -> list[Position]:
    return list(
        (
            await db.execute(
                select(Position).where(Position.agent_id == agent_id, Position.status == "ouverte")
            )
        ).scalars()
    )


async def get_fills(db: AsyncSession, agent_id: str) -> list[Fill]:
    return list(
        (
            await db.execute(
                select(Fill).join(Order, Fill.order_id == Order.id).where(Order.agent_id == agent_id)
            )
        ).scalars()
    )
