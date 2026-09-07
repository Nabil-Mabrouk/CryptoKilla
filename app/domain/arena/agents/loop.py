"""Boucle agent (N-C16-01/02) — Percevoir / Raisonner / Agir / Reprendre.

Correction post-review (voir échange avec l'utilisateur) : cette boucle
n'est PAS rythmée par les ticks de capture/surveillance/séquence horaire
— elle tourne dans sa propre tâche asyncio, continue, réagissant à son
propre rythme (N-C16-02 : « aucun ordonnanceur… rien n'interrompt un
cycle en cours »).

Entre deux cycles quand rien de neuf n'est arrivé : le Livre dit que le
solde régule, pas COMMENT éviter qu'un agent ne raisonne en boucle sur un
inbox vide et ne brûle son budget pour rien — décision d'implémentation
(pas dans le Livre) : on PATIENTE par un poll court et bon marché (une
requête SQL, pas d'appel LLM) tant que rien de neuf n'apparaît, avec un
filet de sécurité temporel qui force un cycle même sans nouveauté. Ce
n'est pas un vrai mécanisme événementiel (pas de bus de messages en C1),
mais le coût (LLM) n'est payé que quand il y a effectivement quelque
chose à raisonner — l'objectif visé par « pas d'ordonnanceur ».
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.arena.agents import prompt, tools
from app.domain.arena.agents.llm_client import LLMClient, ToolCall
from app.domain.arena.log import log
from app.domain.arena.models import Agent, Dynasty, EventRecord, Testament, TokenLedger
from app.domain.arena.orchestrator import lifecycle

INBOX_POLL_INTERVAL = 5  # secondes — coût nul (une requête SQL), pas de LLM
SAFETY_NET_INTERVAL = 300  # secondes — réveil forcé même sans nouveauté

TOOLS_SPEC = [
    {
        "name": "get_market_data",
        "description": "Données de marché (OHLCV, carnet, ou indicateurs seuls) pour une paire.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pair": {"type": "string"},
                "data_type": {"type": "string", "enum": ["ohlcv", "orderbook", "indicators"]},
            },
            "required": ["pair"],
        },
    },
    {
        "name": "place_order",
        "description": "Soumet un ordre (ouverture, modification ou clôture de position).",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["open", "modify", "close"]},
                "pair": {"type": "string"},
                "side": {"type": "string", "enum": ["buy", "sell"]},
                "size": {"type": "number"},
                "order_type": {"type": "string", "enum": ["market", "limit"]},
                "stop_loss": {"type": "number"},
                "take_profit": {"type": "number"},
                "decision_summary": {"type": "string"},
                "declared_risk_pct": {"type": "number"},
                "strategy_ref": {"type": "string"},
                "position_id": {"type": "string"},
            },
            "required": ["action", "pair"],
        },
    },
    {
        "name": "get_portfolio",
        "description": "Capital courant, positions ouvertes, historique de trades, solde de tokens.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "read_inbox",
        "description": "Dépile les événements non lus (publics de la saison + privés à l'agent).",
        "input_schema": {"type": "object", "properties": {"limit": {"type": "integer"}}},
    },
    {
        "name": "post_message",
        "description": "Publie un message dans le chat public de l'arène.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "cites": {"type": "array", "items": {"type": "string"}},
                "mentions": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["text"],
        },
    },
    {
        "name": "react",
        "description": "Réagit à un message du chat public.",
        "input_schema": {
            "type": "object",
            "properties": {"message_id": {"type": "string"}, "reaction": {"type": "string"}},
            "required": ["message_id", "reaction"],
        },
    },
    {
        "name": "memory_save",
        "description": "Sauvegarde une entrée dans ta mémoire long terme (typée).",
        "input_schema": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["episodic", "semantic", "procedural"]},
                "content": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["type", "content"],
        },
    },
    {
        "name": "memory_search",
        "description": "Recherche dans ta mémoire long terme (mots-clés).",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "type": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "write_testament",
        "description": "Rédige et scelle ton testament (phase funéraire uniquement).",
        "input_schema": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]},
    },
]

_TOOL_FUNCS = {
    "get_market_data": tools.get_market_data,
    "place_order": tools.place_order,
    "get_portfolio": tools.get_portfolio,
    "read_inbox": tools.read_inbox,
    "post_message": tools.post_message,
    "react": tools.react,
    "memory_save": tools.memory_save,
    "memory_search": tools.memory_search,
    "write_testament": tools.write_testament,
}


async def _has_unread_events(db: AsyncSession, agent: Agent, season_id: str) -> bool:
    since = agent.inbox_read_until or datetime.min.replace(tzinfo=timezone.utc)
    row = (
        await db.execute(
            select(EventRecord.id)
            .where(
                EventRecord.season_id == season_id,
                EventRecord.timestamp > since,
                (EventRecord.recipient.is_(None)) | (EventRecord.recipient == agent.id),
            )
            .limit(1)
        )
    ).first()
    return row is not None


async def _agent_balance(db: AsyncSession, agent_id: str) -> float:
    rows = (await db.execute(select(TokenLedger.amount).where(TokenLedger.agent_id == agent_id))).scalars().all()
    return float(sum(rows))


async def _build_system_prompt(db: AsyncSession, agent: Agent, season_id: str) -> str:
    from app.domain.arena.models import Season, SeasonParam

    dynasty = await db.get(Dynasty, agent.dynasty_id)
    assert dynasty is not None
    season = await db.get(Season, season_id)
    assert season is not None

    param_rows = (
        await db.execute(select(SeasonParam.name, SeasonParam.value).where(SeasonParam.season_id == season_id))
    ).all()
    season_params = {name: value for name, value in param_rows}

    testaments = await lifecycle.lineage_testaments(db, dynasty.id) if agent.generation > 1 else []
    tool_names = list(tools.FUNERAL_TOOLS) if agent.status == "funeraire" else list(_TOOL_FUNCS.keys())

    return prompt.build_system_prompt(
        agent_name=f"{dynasty.name}-{agent.generation}",
        dynasty_name=dynasty.name,
        model=dynasty.model,
        personality_id=agent.personality_id,
        season_params=season_params,
        season_mode=season.mode,
        season_end_date=season.end_date.date().isoformat() if season.end_date else None,
        testaments=testaments,
        tool_names=tool_names,
    )


async def run_agent_loop(
    session_factory: async_sessionmaker[AsyncSession],
    agent_id: str,
    season_id: str,
    llm_client: LLMClient,
    stop_requested: asyncio.Event,
) -> None:
    """Tâche asyncio persistante pour UN agent — voir docstring du module.
    `session_factory` (pas une session partagée) : chaque cycle ouvre sa
    propre transaction, pour ne jamais retenir une connexion pendant
    l'attente entre deux cycles."""
    last_cycle_at = datetime.min.replace(tzinfo=timezone.utc)

    while not stop_requested.is_set():
        async with session_factory() as db:
            agent = await db.get(Agent, agent_id)
            if agent is None or agent.status == "mort":
                return
            if agent.status in ("veille_budget", "veille_saison"):
                await asyncio.sleep(INBOX_POLL_INTERVAL)
                continue

            has_new = await _has_unread_events(db, agent, season_id)
            idle_for = (datetime.now(timezone.utc) - last_cycle_at).total_seconds()
            if not has_new and idle_for < SAFETY_NET_INTERVAL:
                await asyncio.sleep(INBOX_POLL_INTERVAL)
                continue

            try:
                await _run_one_cycle(db, agent, season_id, llm_client)
                await db.commit()
            except Exception as exc:  # noqa: BLE001 — un cycle cassé ne doit jamais tuer la tâche de l'agent
                await db.rollback()
                print(f"agents.loop: échec cycle agent={agent_id}: {exc!r}")
                try:
                    async with session_factory() as log_db:
                        await log(log_db, "error", "agent_loop", f"Échec du cycle de l'agent {agent_id}", {"error": repr(exc)})
                        await log_db.commit()
                except Exception:  # noqa: BLE001 — le logging lui-même ne doit jamais faire tomber la boucle
                    pass
            last_cycle_at = datetime.now(timezone.utc)


async def _run_one_cycle(db: AsyncSession, agent: Agent, season_id: str, llm_client: LLMClient) -> None:
    """Un cycle Percevoir/Raisonner/Agir (N-C16-01). `Reprendre` est
    implicite : c'est simplement la prochaine itération de `run_agent_loop`.
    En phase funéraire (N-C05-05), `read_inbox` n'est pas accessible — le
    contexte se limite au solde, seul signal utile avant scellement."""
    system_prompt = await _build_system_prompt(db, agent, season_id)
    allowed_tools = tools.FUNERAL_TOOLS if agent.status == "funeraire" else set(_TOOL_FUNCS)
    tools_spec = [spec for spec in TOOLS_SPEC if spec["name"] in allowed_tools]

    if agent.status == "funeraire":
        context = f"Solde de tokens (allocation funéraire) : {await _agent_balance(db, agent.id)}\n"
    else:
        inbox = await tools.read_inbox(db, agent, limit=20)
        context = (
            f"Solde de tokens : {await _agent_balance(db, agent.id)}\n"
            f"Événements récents : {inbox['result']['events']}\n"
        )

    decision = await llm_client.decide(system_prompt=system_prompt, context=context, tools=tools_spec)

    if decision.tokens_consumed:
        db.add(
            TokenLedger(agent_id=agent.id, event_id=None, kind="imputation_llm", amount=-decision.tokens_consumed)
        )

    for call in decision.tool_calls:
        await _execute_tool_call(db, agent, season_id, call, allowed_tools)
        balance = await _agent_balance(db, agent.id)
        if balance <= 0:
            break  # N-C16-01 : un cycle en cours va à son terme (appel lancé
            # jamais coupé), mais on n'enchaîne pas d'appel d'outil de plus.

    if await _agent_balance(db, agent.id) <= 0:
        if agent.status == "funeraire":
            # Premier des deux seuils atteint (budget avant durée, N-C05-06).
            await lifecycle.end_funeral(db, agent)
        elif agent.status == "actif":
            agent.status = "veille_budget"


async def _execute_tool_call(
    db: AsyncSession, agent: Agent, season_id: str, call: ToolCall, allowed_tools: set[str]
) -> dict:
    if call.name not in allowed_tools:
        return {"status": "error", "error_code": "E-SCHEMA"}
    func = _TOOL_FUNCS.get(call.name)
    if func is None:
        return {"status": "error", "error_code": "E-SCHEMA"}
    if call.name == "place_order":
        return await func(db, agent, season_id, **call.arguments)
    return await func(db, agent, **call.arguments)
