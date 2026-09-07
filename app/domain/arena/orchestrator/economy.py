"""Économie — rôle Arbitre (notation, 12.4) + étape 3 de la séquence
horaire (calcul du pool, 12.2).

**Formules explicitement secrètes au Livre (N-C06-08/09) : γ, décote de
réciprocité, rendements décroissants, coefficients α/β.** Aucune valeur
ici ne prétend être un vrai barème de saison 1 — ce sont des `season_params`
éditables, documentées comme illustratives à chaque usage (décision 1 du
plan). Ne JAMAIS lire une valeur en dur : tout passe par `get_param`
(ARENA.md §3).

`classify_message_eligibility` (N-C12-06/07) réutilise l'abstraction
`LLMClient` (décision 2 du plan) : avec `AnthropicLLMClient`, la
classification est un appel outil à schéma fermé (`{classe}`, température
non contrôlable ici mais sortie contrainte — la garantie de forme du
Livre, sortie JSON stricte, est respectée). Sans clé API
(`ScriptedLLMClient`), un classifieur heuristique scripté sert de
remplaçant de test explicite — PAS une vraie classification sémantique.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.agents.llm_client import AnthropicLLMClient, LLMClient
from app.domain.arena.models import Citation, Like, Message, Order, Position, Reaction
from app.domain.arena.params import get_param

EligibilityClass = Literal["substantiel", "contextuel", "vide"]

_CLASSIFY_SYSTEM_PROMPT = """Tu notes un message de chat d'un agent de trading, sans connaître son
auteur (anti-biais, notation sur le contenu seul). Classe-le dans
EXACTEMENT une catégorie parmi : substantiel (analyse, donnée, opinion
argumentée, ou moquerie qui réagit spécifiquement à un contenu précis),
contextuel (réagit au contexte général sans analyse propre, mais n'est pas
du remplissage), vide (spam, remplissage, répétition, hors-sujet).
Réponds en appelant l'outil `submit_classification` avec la classe choisie."""

_CLASSIFY_TOOL_SPEC = [
    {
        "name": "submit_classification",
        "description": "Soumet la classe du message noté.",
        "input_schema": {
            "type": "object",
            "properties": {"classe": {"type": "string", "enum": ["substantiel", "contextuel", "vide"]}},
            "required": ["classe"],
        },
    }
]


def _heuristic_classify(text: str) -> EligibilityClass:
    """Longueur + densité de contenu (décision 2 du plan) — remplaçant de
    test explicite, jamais présenté comme une vraie classification
    sémantique."""
    words = text.split()
    alpha_chars = sum(1 for c in text if c.isalpha())
    density = alpha_chars / max(len(text), 1)

    if len(words) <= 2 or density < 0.3:
        return "vide"
    if len(words) < 8:
        return "contextuel"
    return "substantiel"


async def classify_message_eligibility(llm_client: LLMClient, text: str) -> EligibilityClass:
    if isinstance(llm_client, AnthropicLLMClient):
        decision = await llm_client.decide(system_prompt=_CLASSIFY_SYSTEM_PROMPT, context=text, tools=_CLASSIFY_TOOL_SPEC)
        for call in decision.tool_calls:
            if call.name == "submit_classification":
                classe = call.arguments.get("classe")
                if classe in ("substantiel", "contextuel", "vide"):
                    return classe  # type: ignore[return-value]
        return "vide"  # sortie LLM malformée — traité comme non éligible, jamais une exception qui bloquerait H+0

    return _heuristic_classify(text)


async def classify_pending_messages(db: AsyncSession, llm_client: LLMClient, season_id: str) -> None:
    """Classifie tout message publié sans `eligibility_class` — asynchrone
    par rapport à la publication (N-C12-06), appelé à l'étape 3."""
    rows = (
        await db.execute(select(Message).where(Message.season_id == season_id, Message.eligibility_class.is_(None)))
    ).scalars().all()
    for message in rows:
        message.eligibility_class = await classify_message_eligibility(llm_client, message.text)


def _reciprocity_weight(reaction_index_for_pair: int) -> float:
    """Décote anti-collusion (N-C06-08) — placeholder : chaque réaction
    répétée d'un même réacteur vers le même auteur, DANS la fenêtre,
    compte de moins en moins. Formule réelle secrète (jamais chiffrée par
    le Livre)."""
    return 1.0 / reaction_index_for_pair


def _diminishing_weight(message_index: int, seuil: int) -> float:
    """Rendements décroissants (N-C06-09) — placeholder au-delà du seuil.
    Formule réelle secrète."""
    if message_index <= seuil:
        return 1.0
    return 1.0 / (message_index - seuil + 1)


async def compute_hourly_pool(
    db: AsyncSession, season_id: str, window_start: datetime, window_end: datetime
) -> dict[str, float]:
    """Étape 3 (N-C12-02) : filtre d'éligibilité + points + taille de pool
    + répartition proportionnelle. Retourne `{agent_id: pool_amount}`.

    Le règlement des citations (étape 2) est déjà fait en continu par
    `_settle_close` au moment de la clôture — ici on lit seulement les
    citations créditées dont le trade citant a clôturé DANS cette fenêtre
    (N-C06-06 : « rejoignent la fenêtre qui vient d'être gelée »)."""
    poids_contextuel = await get_param(db, season_id, "poids_message_contextuel", default=0.4)
    seuil_rendement = await get_param(db, season_id, "n_messages_plein_rendement", default=5)
    points_citation = await get_param(db, season_id, "points_par_citation", default=1.0)
    points_like = await get_param(db, season_id, "points_par_like", default=1.0)
    points_reaction = await get_param(db, season_id, "points_par_reaction", default=1.0)
    pool_plancher = await get_param(db, season_id, "pool_plancher", default=0)
    pool_bonus_audience = await get_param(db, season_id, "pool_bonus_audience", default=0)

    messages = (
        await db.execute(
            select(Message)
            .where(
                Message.season_id == season_id,
                Message.created_at >= window_start,
                Message.created_at < window_end,
                Message.eligibility_class.in_(("substantiel", "contextuel")),
            )
            .order_by(Message.agent_id, Message.created_at)
        )
    ).scalars().all()

    agent_points: dict[str, float] = {}
    per_agent_index: dict[str, int] = {}
    reciprocity_seen: dict[tuple[str, str], int] = {}

    for message in messages:
        per_agent_index[message.agent_id] = per_agent_index.get(message.agent_id, 0) + 1
        msg_weight = 1.0 if message.eligibility_class == "substantiel" else poids_contextuel
        msg_weight *= _diminishing_weight(per_agent_index[message.agent_id], seuil_rendement)

        raw_points = 0.0

        likes = (await db.execute(select(Like.id).where(Like.message_id == message.id))).scalars().all()
        raw_points += len(likes) * points_like

        reactions = (
            await db.execute(
                select(Reaction.reactor_agent_id).where(Reaction.target_message_id == message.id)
            )
        ).scalars().all()
        for reactor_id in reactions:
            pair = (reactor_id, message.agent_id)
            reciprocity_seen[pair] = reciprocity_seen.get(pair, 0) + 1
            raw_points += points_reaction * _reciprocity_weight(reciprocity_seen[pair])

        citations = (
            await db.execute(
                select(Citation)
                .join(Order, Citation.order_id == Order.id)
                .join(Position, Order.position_id == Position.id)
                .where(
                    Citation.message_id == message.id,
                    Citation.status == "creditee",
                    Position.closed_at >= window_start,
                    Position.closed_at < window_end,
                )
            )
        ).scalars().all()
        raw_points += len(citations) * points_citation

        agent_points[message.agent_id] = agent_points.get(message.agent_id, 0.0) + raw_points * msg_weight

    total_points = sum(agent_points.values())
    pool_size = pool_plancher + pool_bonus_audience
    if total_points <= 0 or pool_size <= 0:
        # FAQ 6.5 #2 : pas de report, le pool de cette heure est perdu.
        return {}

    return {agent_id: pool_size * points / total_points for agent_id, points in agent_points.items()}
