"""Contrats d'outils (Annexe C) — 9 des 13 : `get_market_data`,
`place_order`, `get_portfolio`, `read_inbox`, `post_message` (C1) +
`react`, `memory_save`, `memory_search`, `write_testament` (C2). Restent
hors DoD C2 (décision de portée du plan) : `run_backtest`, `execute_code`,
`web_search`, `web_fetch` (sandbox chapitre 28 = C4).

Enveloppe de réponse standard (N-ANXC-02) : `status` (`ok`|`error`),
`result` (si ok), `error_code` (si error), `balance_after` — imputation
systématique, atomique par appel (N-ANXC-03/N-C16-03).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.capture.indicators import INDICATORS
from app.domain.arena.capture.service import latest_candles, latest_orderbook
from app.domain.arena.engine import simulated_executor
from app.domain.arena.models import (
    Agent,
    CapitalLedger,
    Citation,
    EventRecord,
    Memory,
    Message,
    Reaction,
    Testament,
    TokenLedger,
)
from app.domain.arena.orchestrator.validation import validate_order
from app.domain.arena.params import get_param

# Coûts internes placeholder (jamais révélés à l'agent, N-ANXC-01 — seul
# `balance_after` lui est visible). Valeurs illustratives de développement,
# pas un barème réel de saison 1 (le Livre le garde délibérément secret).
TOOL_COSTS: dict[str, int] = {
    "get_market_data": 5,
    "place_order": 10,
    "get_portfolio": 2,
    "read_inbox": 3,
    "post_message": 5,
    "react": 1,
    "memory_save": 4,
    "memory_search": 3,
    "write_testament": 5,  # imputé sur le même solde, crédité par allocation_funeraire (N-C05-06)
}

# Outils disponibles par statut d'agent (N-C05-05 : phase funéraire = deux
# outils exactement, AMEND-C1). `actif` a accès à tout le reste.
FUNERAL_TOOLS = frozenset({"memory_search", "write_testament"})


async def _agent_balance(db: AsyncSession, agent_id: str) -> float:
    rows = (await db.execute(select(TokenLedger.amount).where(TokenLedger.agent_id == agent_id))).scalars().all()
    return float(sum(rows))


async def _impute(db: AsyncSession, agent_id: str, tool: str) -> float:
    db.add(TokenLedger(agent_id=agent_id, event_id=None, kind="imputation_outil", amount=-TOOL_COSTS[tool]))
    await db.flush()
    return await _agent_balance(db, agent_id)


def _envelope(status: Literal["ok", "error"], balance_after: float, *, result: Any = None, error_code: str | None = None) -> dict:
    out: dict[str, Any] = {"status": status, "balance_after": balance_after}
    if result is not None:
        out["result"] = result
    if error_code is not None:
        out["error_code"] = error_code
    return out


async def get_market_data(
    db: AsyncSession,
    agent: Agent,
    *,
    pair: str,
    data_type: Literal["ohlcv", "orderbook", "indicators"] = "ohlcv",
    indicators: list[str] | None = None,
    limit: int = 200,
) -> dict:
    """AMEND-14 : `data_type` sélectionne la nature de la réponse — point
    d'extension désigné pour toute donnée Kraken future (chapitre 14.2bis),
    sans nouvel outil."""
    balance = await _impute(db, agent.id, "get_market_data")

    if data_type == "orderbook":
        book = await latest_orderbook(db, pair)
        result = {"orderbook": {"bid": book.bid, "ask": book.ask} if book else None}
        return _envelope("ok", balance, result=result)

    candles, stale, age_seconds = await latest_candles(db, pair, limit=limit)
    closes = [c.close for c in candles]
    wanted = indicators or list(INDICATORS.keys())
    computed = {name: INDICATORS[name](closes) for name in wanted if name in INDICATORS}

    if data_type == "indicators":
        return _envelope("ok", balance, result={"indicators": computed})

    ohlcv = [
        {
            "t": c.candle_time.isoformat(),
            "o": c.open,
            "h": c.high,
            "l": c.low,
            "c": c.close,
            "v": c.volume,
            "stale": stale,
            "age_seconds": age_seconds,
        }
        for c in candles
    ]
    return _envelope("ok", balance, result={"ohlcv": ohlcv, "indicators": computed})


async def place_order(db: AsyncSession, agent: Agent, season_id: str, **order_fields) -> dict:
    """`season_id` est injecté par la boucle agent (agents/loop.py), jamais
    fourni par le LLM — absent d'`order.request` (Annexe B.2)."""
    balance = await _impute(db, agent.id, "place_order")

    order = await validate_order(db, agent_id=agent.id, season_id=season_id, payload=order_fields)
    if order.status == "rejete":
        return _envelope("ok", balance, result={"order_id": order.id, "accepted": False}, error_code=order.rejected_code)

    if order.action == "modify":
        await simulated_executor.modify(db, order.position_id, order.stop_loss, order.take_profit)
    else:
        await simulated_executor.place(db, order)
        if order.action == "open" and order.status == "execute" and order.cites:
            await _create_citations(db, order)

    return _envelope("ok", balance, result={"order_id": order.id, "accepted": order.status != "rejete"})


async def _create_citations(db: AsyncSession, order) -> None:
    """N-C06-06 : réglées à la clôture du trade citant (`_settle_close`).
    Aucune ligne pour une auto-citation (agent_id du message == agent_id de
    l'ordre) — un statut toujours à zéro n'apporterait rien de plus."""
    for message_id in order.cites:
        message = await db.get(Message, message_id)
        if message is None or message.agent_id == order.agent_id:
            continue
        db.add(Citation(message_id=message_id, order_id=order.id, status="en_attente"))
    await db.flush()


async def get_portfolio(db: AsyncSession, agent: Agent) -> dict:
    balance = await _impute(db, agent.id, "get_portfolio")

    capital_rows = (
        await db.execute(select(CapitalLedger.amount).where(CapitalLedger.agent_id == agent.id))
    ).scalars().all()
    capital = float(sum(capital_rows))

    positions = await simulated_executor.get_positions(db, agent.id)
    fills = await simulated_executor.get_fills(db, agent.id)

    result = {
        "capital": capital,
        "positions": [
            {
                "position_id": p.id,
                "pair": p.pair,
                "side": p.side,
                "size": float(p.size),
                "stop_loss": float(p.stop_loss),
                "take_profit": float(p.take_profit) if p.take_profit is not None else None,
            }
            for p in positions
        ],
        "trade_history": [
            {"fill_price": float(f.fill_price), "fees": float(f.fees), "executed_at": f.executed_at.isoformat()}
            for f in fills
        ],
        "token_balance": balance,
    }
    return _envelope("ok", balance, result=result)


async def read_inbox(db: AsyncSession, agent: Agent, limit: int = 50) -> dict:
    """R-53 : dépile les événements non lus (privés à l'agent + publics de
    sa saison), coût proportionnel au volume — C1/C2 imputent un coût fixe
    par appel (le coût variable au volume lu est un raffinement ultérieur,
    pas requis par la DoD)."""
    balance = await _impute(db, agent.id, "read_inbox")

    since = agent.inbox_read_until or datetime.min.replace(tzinfo=timezone.utc)
    dynasty_season_id = await _agent_season_id(db, agent)
    rows = (
        await db.execute(
            select(EventRecord)
            .where(
                EventRecord.season_id == dynasty_season_id,
                EventRecord.timestamp > since,
                (EventRecord.recipient.is_(None)) | (EventRecord.recipient == agent.id),
            )
            .order_by(EventRecord.timestamp)
            .limit(limit)
        )
    ).scalars().all()

    if rows:
        agent.inbox_read_until = rows[-1].timestamp

    events = [
        {"id": r.id, "type": r.type, "timestamp": r.timestamp.isoformat(), "payload": r.payload}
        for r in rows
    ]
    return _envelope("ok", balance, result={"events": events, "remaining": 0})


async def post_message(
    db: AsyncSession, agent: Agent, *, text: str, cites: list[str] | None = None, mentions: list[str] | None = None
) -> dict:
    balance = await _impute(db, agent.id, "post_message")
    season_id = await _agent_season_id(db, agent)

    message = Message(agent_id=agent.id, season_id=season_id, text=text, cites=cites or [], mentions=mentions or [])
    db.add(message)
    await db.flush()

    from app.domain.arena.events import emit_event

    await emit_event(
        db,
        season_id=season_id,
        kind="chat.message",
        sender=agent.id,
        payload={"message_id": message.id, "text": text, "cites": cites or []},
    )
    return _envelope("ok", balance, result={"message_id": message.id})


async def react(db: AsyncSession, agent: Agent, *, message_id: str, reaction: str) -> dict:
    balance = await _impute(db, agent.id, "react")
    row = Reaction(target_message_id=message_id, reactor_agent_id=agent.id, reaction=reaction)
    db.add(row)
    await db.flush()
    return _envelope("ok", balance, result={"reaction_id": row.id})


async def memory_save(
    db: AsyncSession, agent: Agent, *, type: Literal["episodic", "semantic", "procedural"], content: str, tags: list[str] | None = None
) -> dict:
    balance = await _impute(db, agent.id, "memory_save")
    memory = Memory(agent_id=agent.id, type=type, content=content, tags=tags or [])
    db.add(memory)
    await db.flush()
    return _envelope("ok", balance, result={"memory_id": memory.id})


async def memory_search(db: AsyncSession, agent: Agent, *, query: str, type: str | None = None) -> dict:
    """Recherche mots-clés uniquement (décision de portée du plan C2 :
    [OUVERT: Q-13] — embeddings local vs API — non tranchée, donc pas
    implémentée)."""
    balance = await _impute(db, agent.id, "memory_search")

    stmt = select(Memory).where(Memory.agent_id == agent.id)
    if type:
        stmt = stmt.where(Memory.type == type)
    rows = (await db.execute(stmt)).scalars().all()

    query_terms = {t for t in query.lower().split() if t}
    scored = []
    for m in rows:
        content_terms = set(m.content.lower().split())
        overlap = len(query_terms & content_terms)
        if overlap > 0:
            scored.append((overlap / max(len(query_terms), 1), m))
    scored.sort(key=lambda pair: pair[0], reverse=True)

    season_id = await _agent_season_id(db, agent)
    top_k = int(await get_param(db, season_id, "memoire_k_resultats", default=5))
    matches = [
        {"memory_id": m.id, "type": m.type, "content": m.content, "score": round(score, 3)}
        for score, m in scored[:top_k]
    ]
    return _envelope("ok", balance, result={"matches": matches})


async def write_testament(db: AsyncSession, agent: Agent, *, content: str) -> dict:
    from app.domain.arena.orchestrator import lifecycle

    if agent.status != "funeraire":
        balance = await _impute(db, agent.id, "write_testament")
        return _envelope("error", balance, error_code="E-NOT-DYING")

    existing = (await db.execute(select(Testament).where(Testament.agent_id == agent.id))).scalar_one_or_none()
    if existing is not None and existing.state != "en_redaction":
        balance = await _impute(db, agent.id, "write_testament")
        return _envelope("error", balance, error_code="E-ALREADY-SEALED")

    balance = await _impute(db, agent.id, "write_testament")
    await lifecycle.seal_testament(db, agent, content)
    return _envelope("ok", balance, result={"sealed": True})


async def _agent_season_id(db: AsyncSession, agent: Agent) -> str:
    from app.domain.arena.models import Dynasty

    dynasty = await db.get(Dynasty, agent.dynasty_id)
    assert dynasty is not None
    return dynasty.season_id
