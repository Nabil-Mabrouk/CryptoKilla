"""Routeurs métier de cryptokilla (généré depuis domain_routes).

Un APIRouter par route déclarée, avec un endpoint stub à implémenter. Le core
inclut ces routeurs sous app/domain/ (Chap 3/5). Ne pas éditer pour un besoin
partagé : modifier le template puis `copier update`.
"""

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import require_admin
from app.core.database import get_db
from app.core.models import User
from app.domain.arena.log import log as arena_log
from app.domain.arena.models import (
    Agent,
    ArenaLog,
    CapitalLedger,
    Dynasty,
    EventRecord,
    Position,
    Season,
    SeasonParam,
    TokenLedger,
)
from app.domain.arena.provisioning import create_dynasty, create_season

arena_router = APIRouter(prefix="/api/arena", tags=["arena"])


class CreateSeasonRequest(BaseModel):
    mode: Literal["datee", "perpetuelle"] = "perpetuelle"
    params: dict[str, Any] | None = None


class CreateDynastyRequest(BaseModel):
    name: str
    model: str
    color: str


class UpdateParamRequest(BaseModel):
    value: Any


@arena_router.get("/status")
async def arena_status(db: AsyncSession = Depends(get_db), _admin: User = Depends(require_admin)) -> dict:
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


# ==================================================================
# Console admin — créer une saison/des dynasties, observer événements
# et erreurs. Tous protégés par require_admin.
# ==================================================================


@arena_router.post("/admin/seasons")
async def admin_create_season(
    body: CreateSeasonRequest, db: AsyncSession = Depends(get_db), _admin: User = Depends(require_admin)
) -> dict:
    season = await create_season(db, mode=body.mode, params_overrides=body.params)
    await arena_log(db, "info", "admin", f"Saison {season.id} créée", {"mode": body.mode})
    await db.commit()
    return {"id": season.id, "state": season.state, "mode": season.mode}


@arena_router.get("/admin/seasons")
async def admin_list_seasons(db: AsyncSession = Depends(get_db), _admin: User = Depends(require_admin)) -> list[dict]:
    seasons = (await db.execute(select(Season).order_by(Season.created_at.desc()))).scalars().all()
    out = []
    for s in seasons:
        dynasty_ids = [row[0] for row in (await db.execute(select(Dynasty.id).where(Dynasty.season_id == s.id))).all()]
        agent_count = 0
        if dynasty_ids:
            agent_count = len(
                (await db.execute(select(Agent.id).where(Agent.dynasty_id.in_(dynasty_ids)))).all()
            )
        out.append(
            {
                "id": s.id,
                "state": s.state,
                "mode": s.mode,
                "created_at": s.created_at.isoformat(),
                "dynasty_count": len(dynasty_ids),
                "agent_count": agent_count,
            }
        )
    return out


@arena_router.get("/admin/seasons/{season_id}/params")
async def admin_get_params(
    season_id: str, db: AsyncSession = Depends(get_db), _admin: User = Depends(require_admin)
) -> list[dict]:
    rows = (await db.execute(select(SeasonParam).where(SeasonParam.season_id == season_id))).scalars().all()
    return [{"name": r.name, "value": r.value, "visibility": r.visibility} for r in rows]


@arena_router.patch("/admin/seasons/{season_id}/params/{name}")
async def admin_update_param(
    season_id: str,
    name: str,
    body: UpdateParamRequest,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> dict:
    param = await db.get(SeasonParam, {"season_id": season_id, "name": name})
    if param is None:
        raise HTTPException(status_code=404, detail="Paramètre introuvable")
    param.value = body.value
    await arena_log(db, "info", "admin", f"Paramètre {name} modifié", {"season_id": season_id, "value": body.value})
    await db.commit()
    return {"name": name, "value": body.value}


@arena_router.post("/admin/seasons/{season_id}/dynasties")
async def admin_create_dynasty(
    season_id: str,
    body: CreateDynastyRequest,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> dict:
    season = await db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Saison introuvable")
    dynasty = await create_dynasty(db, season_id=season_id, name=body.name, model=body.model, color=body.color)
    await arena_log(db, "info", "admin", f"Dynastie {body.name} créée", {"season_id": season_id})
    await db.commit()
    return {"id": dynasty.id, "name": dynasty.name}


@arena_router.get("/admin/seasons/{season_id}/dynasties")
async def admin_list_dynasties(
    season_id: str, db: AsyncSession = Depends(get_db), _admin: User = Depends(require_admin)
) -> list[dict]:
    dynasties = (await db.execute(select(Dynasty).where(Dynasty.season_id == season_id))).scalars().all()
    out = []
    for dynasty in dynasties:
        agents = (await db.execute(select(Agent).where(Agent.dynasty_id == dynasty.id))).scalars().all()
        agent_rows = []
        for a in agents:
            capital = float(
                sum((await db.execute(select(CapitalLedger.amount).where(CapitalLedger.agent_id == a.id))).scalars())
            )
            tokens = float(
                sum((await db.execute(select(TokenLedger.amount).where(TokenLedger.agent_id == a.id))).scalars())
            )
            agent_rows.append(
                {"id": a.id, "generation": a.generation, "status": a.status, "capital": capital, "token_balance": tokens}
            )
        out.append(
            {"id": dynasty.id, "name": dynasty.name, "model": dynasty.model, "color": dynasty.color, "agents": agent_rows}
        )
    return out


@arena_router.get("/admin/events")
async def admin_list_events(
    season_id: str | None = None,
    type: str | None = None,
    sender: str | None = None,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[dict]:
    stmt = select(EventRecord).order_by(EventRecord.timestamp.desc()).limit(limit)
    if season_id:
        stmt = stmt.where(EventRecord.season_id == season_id)
    if type:
        stmt = stmt.where(EventRecord.type == type)
    if sender:
        stmt = stmt.where(EventRecord.sender == sender)
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": r.id,
            "type": r.type,
            "timestamp": r.timestamp.isoformat(),
            "sender": r.sender,
            "recipient": r.recipient,
            "payload": r.payload,
        }
        for r in rows
    ]


@arena_router.get("/admin/logs")
async def admin_list_logs(
    level: str | None = None,
    limit: int = Query(default=100, le=500),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[dict]:
    stmt = select(ArenaLog).order_by(ArenaLog.created_at.desc()).limit(limit)
    if level:
        stmt = stmt.where(ArenaLog.level == level)
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "level": r.level,
            "component": r.component,
            "message": r.message,
            "details": r.details,
        }
        for r in rows
    ]


# ==================================================================
# Lecture publique — tranche minimale (pas d'authentification) pour que
# la landing reflète honnêtement une saison réellement créée, sans
# anticiper la couche C3 (pas de chat, pas de WebSocket, pas de Killa).
#
# Périmètre volontairement restreint à ce qu'ARENA.md §3 autorise déjà à
# publier : classement (chapitre 24.1, "recalculable depuis l'historique
# public"), dynasties, statut de saison. RIEN de secret n'y transite —
# jamais les season_params `visibility: secret` (coefficients de fill,
# plancher/bonus du pool), jamais un testament non publié.
# ==================================================================


@arena_router.get("/public/status")
async def arena_public_status(db: AsyncSession = Depends(get_db)) -> dict:
    season = (
        await db.execute(select(Season).where(Season.state == "active").order_by(Season.created_at.desc()).limit(1))
    ).scalar_one_or_none()
    if season is None:
        return {"season": None, "alive_count": 0, "dynasties": [], "leaderboard": []}

    dynasties = (await db.execute(select(Dynasty).where(Dynasty.season_id == season.id))).scalars().all()
    dynasty_by_id = {d.id: d for d in dynasties}

    agents = (
        await db.execute(select(Agent).where(Agent.dynasty_id.in_(dynasty_by_id.keys())))
        if dynasty_by_id
        else None
    )
    agents = agents.scalars().all() if agents is not None else []

    leaderboard = []
    alive_count = 0
    for agent in agents:
        if agent.status != "mort":
            alive_count += 1
        capital_rows = (
            await db.execute(select(CapitalLedger.amount).where(CapitalLedger.agent_id == agent.id))
        ).scalars().all()
        capital = float(sum(capital_rows))
        pnl_rows = (
            await db.execute(
                select(CapitalLedger.amount).where(
                    CapitalLedger.agent_id == agent.id, CapitalLedger.kind.in_(("pnl_realise", "frais"))
                )
            )
        ).scalars().all()
        pnl = float(sum(pnl_rows))
        dynasty = dynasty_by_id[agent.dynasty_id]
        leaderboard.append(
            {
                "dynasty": dynasty.name,
                "color": dynasty.color,
                "generation": agent.generation,
                "status": agent.status,
                "capital": capital,
                "pnl": pnl,
            }
        )
    leaderboard.sort(key=lambda row: row["capital"], reverse=True)

    return {
        "season": {"id": season.id, "state": season.state, "mode": season.mode},
        "alive_count": alive_count,
        "dynasties": [{"name": d.name, "model": d.model, "color": d.color} for d in dynasties],
        "leaderboard": leaderboard,
    }
