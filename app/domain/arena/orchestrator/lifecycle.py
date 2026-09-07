"""Cycle de vie — chapitre 5, rôle Arbitre de l'orchestrateur (12.1.3).

Trois points d'entrée, chacun correspondant à une décision de portée du
plan C2 :
- `check_death` : appelé uniquement après `_settle_close` (le capital ne
  change jamais ailleurs, décision 6) — constat en continu (N-C05-03).
- `check_funeral_expirations` : appelé à chaque tick (~30s, décision 7),
  scelle le testament au premier des deux seuils atteint (budget ou durée,
  N-C05-06) — le seuil budget est en pratique déjà couvert par
  `agents/loop.py` (solde épuisé après un appel d'outil funéraire), ce
  point-ci ne couvre que la durée.
- `process_rebirths` : appelé à l'étape 5 de la séquence horaire
  (N-C12-02), jamais ailleurs — seule la renaissance est réglée à l'heure
  pleine, la mort est continue (N-C12-03).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.events import emit_event
from app.domain.arena.models import (
    Agent,
    CapitalLedger,
    Dynasty,
    Testament,
    TokenLedger,
)
from app.domain.arena.params import get_param


def _aware(value: datetime) -> datetime:
    """SQLite (tests, `aiosqlite`) rend un `DateTime(timezone=True)` peuplé
    par `server_default=func.now()` sans tzinfo après un aller-retour DB —
    Postgres (prod, AMEND-03) le garde aware. Normalise en UTC avant toute
    arithmétique pour rester correct dans les deux cas."""
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


async def _agent_season_id(db: AsyncSession, agent: Agent) -> str:
    dynasty = await db.get(Dynasty, agent.dynasty_id)
    assert dynasty is not None
    return dynasty.season_id


async def _agent_capital(db: AsyncSession, agent_id: str) -> float:
    rows = (await db.execute(select(CapitalLedger.amount).where(CapitalLedger.agent_id == agent_id))).scalars().all()
    return float(sum(rows))


async def check_death(db: AsyncSession, agent: Agent) -> bool:
    """Retourne `True` si l'agent vient de basculer en phase funéraire.
    Ne fait rien si l'agent n'est pas `actif` (idempotent — un agent déjà
    funéraire/mort ne peut pas mourir deux fois)."""
    if agent.status != "actif":
        return False

    season_id = await _agent_season_id(db, agent)
    seuil_mort = await get_param(db, season_id, "seuil_mort", default=0)
    capital = await _agent_capital(db, agent.id)
    if capital > seuil_mort:
        return False

    await _enter_funeral(db, agent, season_id)
    return True


async def _enter_funeral(db: AsyncSession, agent: Agent, season_id: str) -> None:
    agent.status = "funeraire"
    agent.died_at = datetime.now(timezone.utc)

    event = await emit_event(
        db,
        season_id=season_id,
        kind="agent.death",
        sender=agent.id,
        payload={"agent_id": agent.id, "died_at": agent.died_at.isoformat()},
    )

    allocation = await get_param(db, season_id, "allocation_funeraire", default=0)
    if allocation:
        db.add(TokenLedger(agent_id=agent.id, event_id=event.id, kind="allocation_funeraire", amount=allocation))


async def seal_testament(db: AsyncSession, agent: Agent, content: str | None) -> Testament:
    """Scelle le CONTENU du testament — y compris vide (`content=None`,
    N-C05-06). Idempotent : un testament déjà scellé n'est jamais réécrit
    (appelable une seule fois, N-C21-02). Ne touche PAS `agent.status` :
    un agent peut sceller tôt (`write_testament`) et rester `funeraire`
    jusqu'à l'épuisement du budget ou de la durée — voir `end_funeral`,
    seul point qui fait passer l'agent à `mort`. Séparer les deux rend
    `E-ALREADY-SEALED` (Annexe C) atteignable indépendamment de
    `E-NOT-DYING` : sans cette séparation, un testament scellé impliquerait
    déjà `agent.status == 'mort'`, et `E-NOT-DYING` masquerait toujours
    `E-ALREADY-SEALED` (décision d'implémentation, pas dans le Livre)."""
    testament = (await db.execute(select(Testament).where(Testament.agent_id == agent.id))).scalar_one_or_none()
    if testament is None:
        testament = Testament(agent_id=agent.id)
        db.add(testament)
        await db.flush()

    if testament.state != "en_redaction":
        return testament

    if content is not None:
        season_id = await _agent_season_id(db, agent)
        taille_max = await get_param(db, season_id, "taille_max_testament", default=2_000)
        testament.content = content[:taille_max]

    testament.state = "scelle"
    testament.sealed_at = datetime.now(timezone.utc)
    return testament


async def end_funeral(db: AsyncSession, agent: Agent) -> None:
    """Fin de la phase funéraire — budget OU durée épuisés, le premier des
    deux atteint (N-C05-06). Scelle le testament s'il ne l'est pas déjà
    (vide si jamais rédigé), puis fait passer l'agent à `mort` (terminal,
    seule transition possible depuis `funeraire`)."""
    if agent.status != "funeraire":
        return
    await seal_testament(db, agent, content=None)
    agent.status = "mort"


async def check_funeral_expirations(db: AsyncSession, season_id: str) -> None:
    """Vérifié à chaque tick (~30s) — `duree_max_funeraire` est trop fine
    pour une vérification horaire (décision 7 du plan). Le seuil budget
    est couvert ailleurs (`agents/loop.py`, cycle de raisonnement)."""
    duree_max = await get_param(db, season_id, "duree_max_funeraire", default=1_800)
    now = datetime.now(timezone.utc)

    agents = (
        await db.execute(
            select(Agent)
            .join(Dynasty, Agent.dynasty_id == Dynasty.id)
            .where(Dynasty.season_id == season_id, Agent.status == "funeraire")
        )
    ).scalars().all()

    for agent in agents:
        if agent.died_at is None:
            continue
        if (now - _aware(agent.died_at)).total_seconds() >= duree_max:
            await end_funeral(db, agent)

    await db.commit()


async def lineage_testaments(db: AsyncSession, dynasty_id: str) -> list[dict]:
    """Héritage cumulé (chapitre 9.3, N-C05-08) : concaténation
    chronologique de TOUS les testaments scellés/publiés de la lignée,
    jamais ceux d'une autre dynastie (N-C18-04)."""
    rows = (
        await db.execute(
            select(Agent, Testament)
            .join(Testament, Testament.agent_id == Agent.id)
            .where(Agent.dynasty_id == dynasty_id, Testament.state.in_(("scelle", "publie")))
            .order_by(Agent.generation)
        )
    ).all()

    dynasty = await db.get(Dynasty, dynasty_id)
    assert dynasty is not None

    entries = []
    for agent, testament in rows:
        pnl_rows = (
            await db.execute(
                select(CapitalLedger.amount).where(
                    CapitalLedger.agent_id == agent.id, CapitalLedger.kind != "capital_initial"
                )
            )
        ).scalars().all()
        pnl_final = float(sum(pnl_rows))
        hours_alive = (
            (_aware(agent.died_at) - _aware(agent.born_at)).total_seconds() / 3600 if agent.died_at else 0.0
        )
        entries.append(
            {
                "agent_name": f"{dynasty.name}-{agent.generation}",
                "died_at": agent.died_at.date().isoformat() if agent.died_at else "?",
                "cause": "capital épuisé",  # seul déclencheur de mort implémenté (décision 6 du plan)
                "hours_alive": round(hours_alive),
                "pnl_final": round(pnl_final, 2),
                "content": testament.content,
            }
        )
    return entries


async def process_rebirths(db: AsyncSession, season_id: str) -> None:
    """Étape 5 de la séquence horaire (N-C12-02) — uniquement les
    renaissances arrivées à échéance de `delai_renaissance`, compté depuis
    `died_at` (constat de mort continu, N-C05-03 ; le testament est
    garanti scellé avant l'échéance dès lors que `delai_renaissance >=
    duree_max_funeraire`, sinon la renaissance attend simplement le
    prochain H+0 où l'agent sera passé `mort` — délai bénin, pas un bug)."""
    delai = await get_param(db, season_id, "delai_renaissance", default=3_600)
    capital_initial = await get_param(db, season_id, "capital_initial", default=0)
    now = datetime.now(timezone.utc)

    dead_agents = (
        await db.execute(
            select(Agent)
            .join(Dynasty, Agent.dynasty_id == Dynasty.id)
            .where(Dynasty.season_id == season_id, Agent.status == "mort")
        )
    ).scalars().all()

    for agent in dead_agents:
        if agent.died_at is None or (now - _aware(agent.died_at)).total_seconds() < delai:
            continue

        existing_successor = (
            await db.execute(
                select(Agent.id).where(
                    Agent.dynasty_id == agent.dynasty_id, Agent.generation == agent.generation + 1
                )
            )
        ).first()
        if existing_successor is not None:
            continue

        successor = Agent(
            dynasty_id=agent.dynasty_id,
            generation=agent.generation + 1,
            # [OUVERT : Q-11] non tranchée par le Livre — décision
            # d'implémentation (pas de lore) : reconduit la même
            # personnalité par défaut (voir agents/prompt.py).
            personality_id=agent.personality_id,
            status="actif",
        )
        db.add(successor)
        await db.flush()

        birth_event = await emit_event(
            db,
            season_id=season_id,
            kind="agent.birth",
            sender="orchestrator",
            payload={"agent_id": successor.id, "generation": successor.generation, "dynasty_id": agent.dynasty_id},
        )
        db.add(CapitalLedger(agent_id=successor.id, event_id=birth_event.id, kind="capital_initial", amount=capital_initial))

        # N-C12-13 : allocation initiale immédiate, le nouveau-né n'attend
        # pas l'étape 4 (déjà passée pour les agents vivants AVANT le gel).
        base_amount = await get_param(db, season_id, "allocation_horaire_par_modele", default=0)
        if base_amount:
            alloc_event = await emit_event(
                db,
                season_id=season_id,
                kind="tokens.allocation",
                sender="orchestrator",
                recipient=successor.id,
                payload={"base_amount": base_amount, "pool_amount": 0, "new_balance": base_amount},
            )
            db.add(TokenLedger(agent_id=successor.id, event_id=alloc_event.id, kind="allocation_base", amount=base_amount))
        # Héritage cumulé (chapitre 9.3) : pas stocké côté agent, assemblé
        # à la volée par `lineage_testaments` au moment de construire le
        # prompt système (agents/loop.py) — une seule source de vérité.
