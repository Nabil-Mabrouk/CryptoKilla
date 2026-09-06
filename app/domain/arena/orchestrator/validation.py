"""Pipeline de validation — Garde-fou (N-C12-01/04), 3 branches par
`action` (AMEND-B1/AMEND-12). Déterministe, jamais de LLM ici (N-C12-01).

Chaque branche s'arrête au premier code d'erreur rencontré (N-C12-05) ;
`order.rejected` porte exactement un `error_code`. Un ordre qui franchit
toute sa branche est transmis au moteur (`engine.simulated_executor`),
JAMAIS exécuté ici — cette séparation est ce qui permet au moteur de
revalider la liquidité au moment du fill (double garde, N-C12-16/N-C13-11).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.capture.service import latest_candles, latest_orderbook
from app.domain.arena.engine import fill_model
from app.domain.arena.events import emit_event
from app.domain.arena.models import CapitalLedger, Order, Position, Season
from app.domain.arena.params import get_param


class OrderRejected(Exception):
    def __init__(self, code: str, detail: str = ""):
        self.code = code
        self.detail = detail
        super().__init__(code)


async def _agent_capital(db: AsyncSession, agent_id: str) -> float:
    rows = (await db.execute(select(CapitalLedger.amount).where(CapitalLedger.agent_id == agent_id))).scalars().all()
    return float(sum(rows))


async def _open_position(db: AsyncSession, agent_id: str, pair: str) -> Position | None:
    return (
        await db.execute(
            select(Position).where(Position.agent_id == agent_id, Position.pair == pair, Position.status == "ouverte")
        )
    ).scalar_one_or_none()


async def _kill_switch_engaged(db: AsyncSession, season_id: str) -> bool:
    season = await db.get(Season, season_id)
    return season is None or season.state != "active"


async def _reference_price_for_risk(db: AsyncSession, pair: str) -> float | None:
    book = await latest_orderbook(db, pair)
    if book is None:
        return None
    return (book.bid + book.ask) / 2


async def validate_order(db: AsyncSession, *, agent_id: str, season_id: str, payload: dict) -> Order:
    """Crée et persiste l'`Order` (statut `accepte` ou `rejete` selon
    l'issue) — jamais exécuté ici. `payload` = champs d'un `order.request`
    (Annexe B.2)."""
    order = Order(
        agent_id=agent_id,
        season_id=season_id,
        action=payload["action"],
        pair=payload.get("pair"),
        side=payload.get("side"),
        size=payload.get("size"),
        order_type=payload.get("order_type"),
        limit_price=payload.get("limit_price"),
        stop_loss=payload.get("stop_loss"),
        take_profit=payload.get("take_profit"),
        decision_summary=payload.get("decision_summary"),
        cites=payload.get("cites"),
        position_id=payload.get("position_id"),
        declared_risk_pct=payload.get("declared_risk_pct"),
        strategy_ref=payload.get("strategy_ref"),
        status="soumis",
    )
    db.add(order)
    await db.flush()

    try:
        if order.action == "open":
            await _validate_open(db, order)
        elif order.action == "modify":
            await _validate_modify(db, order)
        elif order.action == "close":
            await _validate_close(db, order)
        else:
            raise OrderRejected("E-SCHEMA", f"action inconnue : {order.action}")
        order.status = "accepte"
    except OrderRejected as rejected:
        order.status = "rejete"
        order.rejected_code = rejected.code
        await emit_event(
            db,
            season_id=season_id,
            kind="order.rejected",
            sender="orchestrator",
            recipient=agent_id,
            payload={"order_id": order.id, "error_code": rejected.code, "detail": rejected.detail},
        )
    return order


async def _validate_open(db: AsyncSession, order: Order) -> None:
    if await _kill_switch_engaged(db, order.season_id):
        raise OrderRejected("E-KILL-SWITCH", "Saison non active.")

    liste_paires = await get_param(db, order.season_id, "liste_paires", default=[])
    if order.pair not in liste_paires:
        raise OrderRejected("E-PAIR-UNKNOWN", f"{order.pair} n'est pas dans liste_paires.")

    if order.stop_loss is None:
        raise OrderRejected("E-NO-STOP", "stop_loss obligatoire pour action=open (R-41).")

    if await _open_position(db, order.agent_id, order.pair) is not None:
        raise OrderRejected("E-POSITION-EXISTS", "Position déjà ouverte sur cette paire.")

    capital = await _agent_capital(db, order.agent_id)
    size = float(order.size or 0)
    if size > capital:
        raise OrderRejected("E-INSUFFICIENT-CAPITAL", "Capital insuffisant.")

    taille_max_ordre = await get_param(db, order.season_id, "taille_max_ordre", default=float("inf"))
    if size > taille_max_ordre:
        raise OrderRejected("E-SIZE-EXCEEDED", "Taille au-delà de taille_max_ordre.")

    ref = await _reference_price_for_risk(db, order.pair)
    if ref is not None and order.stop_loss is not None:
        distance = abs(ref - float(order.stop_loss)) / ref
        potential_loss = size * distance
        risk_pct = (potential_loss / capital * 100) if capital > 0 else float("inf")
        order.risk_calculated_pct = risk_pct
        risque_max_trade = await get_param(db, order.season_id, "risque_max_trade", default=100)
        if risk_pct > risque_max_trade:
            raise OrderRejected("E-RISK-EXCEEDED", "Perte potentielle au stop > risque_max_trade.")

    candles, stale, _age = await latest_candles(db, order.pair, limit=60)
    if ref is not None and not stale and candles:
        volume_1h = sum(c.volume for c in candles) * ref
        part_max_liquidite = await get_param(db, order.season_id, "part_max_liquidite", default=0.05)
        if not fill_model.check_liquidity(size, volume_1h, part_max_liquidite):
            raise OrderRejected("E-LIQUIDITY", "Taille au-delà de la liquidité horaire disponible.")
    # Transmission au moteur : voir orchestrator/hourly.py ou le point
    # d'appel de la boucle agent (agents/loop.py), qui appelle
    # engine.simulated_executor.place() sur un Order `accepte`.


async def _validate_modify(db: AsyncSession, order: Order) -> None:
    if await _kill_switch_engaged(db, order.season_id):
        raise OrderRejected("E-KILL-SWITCH", "Saison non active.")

    position = await db.get(Position, order.position_id) if order.position_id else None
    if position is None or position.status != "ouverte" or position.agent_id != order.agent_id:
        raise OrderRejected("E-POSITION-UNKNOWN", "Position introuvable ou non ouverte.")

    if order.stop_loss is not None:
        current_stop = float(position.stop_loss)
        new_stop = float(order.stop_loss)
        tightened = new_stop > current_stop if position.side == "buy" else new_stop < current_stop
        if not tightened:
            raise OrderRejected("E-STOP-WIDENING", "Un stop ne peut être qu'resserré (ch.7.2).")

        ref = await _reference_price_for_risk(db, position.pair)
        if ref is not None:
            capital = await _agent_capital(db, order.agent_id)
            distance = abs(ref - new_stop) / ref
            risk_pct = (float(position.size) * distance / capital * 100) if capital > 0 else float("inf")
            risque_max_trade = await get_param(db, order.season_id, "risque_max_trade", default=100)
            if risk_pct > risque_max_trade:
                raise OrderRejected("E-RISK-EXCEEDED", "Nouveau stop dépasse risque_max_trade.")

    # Pas de trade.opened/trade.closed pour une modification (N-C12-14) —
    # appliqué directement par l'appelant via engine.simulated_executor.modify().


async def _validate_close(db: AsyncSession, order: Order) -> None:
    if await _kill_switch_engaged(db, order.season_id):
        raise OrderRejected("E-KILL-SWITCH", "Saison non active.")

    position = await db.get(Position, order.position_id) if order.position_id else None
    if position is None or position.status != "ouverte" or position.agent_id != order.agent_id:
        raise OrderRejected("E-POSITION-UNKNOWN", "Position introuvable ou non ouverte.")
