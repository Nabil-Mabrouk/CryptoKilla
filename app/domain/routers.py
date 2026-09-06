"""Routeurs métier de cryptokilla (généré depuis domain_routes).

Un APIRouter par route déclarée, avec un endpoint stub à implémenter. Le core
inclut ces routeurs sous app/domain/ (Chap 3/5). Ne pas éditer pour un besoin
partagé : modifier le template puis `copier update`.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.arena.models import Agent, CapitalLedger, EventRecord, Position, TokenLedger

# Lecture seule, sans authentification pour l'instant (C1 : vérification
# manuelle en dev, pas une API publique documentée) — expose le strict
# minimum pour confirmer que le worker tourne sans passer par psql.
arena_router = APIRouter(prefix="/api/arena", tags=["arena"])


@arena_router.get("/status")
async def arena_status(db: AsyncSession = Depends(get_db)) -> dict:
    agent = (await db.execute(select(Agent).where(Agent.status != "mort").limit(1))).scalar_one_or_none()
    if agent is None:
        return {"agent": None}

    capital = float(
        sum((await db.execute(select(CapitalLedger.amount).where(CapitalLedger.agent_id == agent.id))).scalars())
    )
    tokens = float(
        sum((await db.execute(select(TokenLedger.amount).where(TokenLedger.agent_id == agent.id))).scalars())
    )
    positions = (
        await db.execute(select(Position).where(Position.agent_id == agent.id, Position.status == "ouverte"))
    ).scalars().all()
    last_bulletin = (
        await db.execute(
            select(EventRecord)
            .where(EventRecord.type == "market.bulletin")
            .order_by(EventRecord.timestamp.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    return {
        "agent": {"id": agent.id, "status": agent.status, "capital": capital, "token_balance": tokens},
        "open_positions": [
            {"pair": p.pair, "side": p.side, "size": float(p.size), "stop_loss": float(p.stop_loss)}
            for p in positions
        ],
        "last_bulletin": last_bulletin.payload if last_bulletin else None,
    }


