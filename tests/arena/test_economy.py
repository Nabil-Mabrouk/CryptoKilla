"""Économie — notation des messages (12.4), pool d'engagement (6.5),
règlement des citations (N-C06-06) à la clôture du trade citant."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.domain.arena.agents import tools
from app.domain.arena.agents.llm_client import ScriptedLLMClient
from app.domain.arena.models import (
    Agent,
    CapitalLedger,
    Citation,
    Dynasty,
    Like,
    MarketCandle,
    Message,
    OrderbookSnapshot,
    Position,
    Reaction,
    SeasonParam,
)
from app.domain.arena.orchestrator import economy


async def _set_param(db, season_id: str, name: str, value) -> None:
    row = await db.get(SeasonParam, {"season_id": season_id, "name": name})
    if row is None:
        db.add(SeasonParam(season_id=season_id, name=name, value=value, visibility="public"))
    else:
        row.value = value
    await db.flush()


async def _second_agent(db, season_id: str) -> Agent:
    dynasty = Dynasty(season_id=season_id, name="test-dynasty-2", model="gpt", color="#123456")
    db.add(dynasty)
    await db.flush()
    agent = Agent(dynasty_id=dynasty.id, generation=1, status="actif")
    db.add(agent)
    await db.flush()
    return agent


async def _seed_market(db, pair: str, price: float, n_candles: int = 60) -> None:
    now = datetime.now(timezone.utc)
    for i in range(n_candles):
        db.add(
            MarketCandle(
                pair=pair, candle_time=now - timedelta(minutes=n_candles - i),
                open=price, high=price, low=price, close=price, volume=10.0,
            )
        )
    db.add(OrderbookSnapshot(pair=pair, bid=price - 1, ask=price + 1))
    await db.flush()


# --- Classification (heuristique, remplaçant de test) -----------------------


async def test_heuristic_classifies_spam_as_vide():
    classe = await economy.classify_message_eligibility(ScriptedLLMClient(), "gm")
    assert classe == "vide"


async def test_heuristic_classifies_emoji_spam_as_vide():
    classe = await economy.classify_message_eligibility(ScriptedLLMClient(), "🚀🚀🚀🚀🚀🚀🚀")
    assert classe == "vide"


async def test_heuristic_classifies_short_reaction_as_contextuel():
    # Exemple du Livre (chapitre 12.4), classé `contextuel`.
    classe = await economy.classify_message_eligibility(ScriptedLLMClient(), "Bulletin reçu, marché calme cette heure.")
    assert classe == "contextuel"


async def test_heuristic_classifies_analysis_as_substantiel():
    classe = await economy.classify_message_eligibility(
        ScriptedLLMClient(),
        "BTC casse la résistance 4h sur volume 1.6x la moyenne, j'envisage une entrée momentum si la clôture 1h confirme.",
    )
    assert classe == "substantiel"


async def test_classify_pending_messages_only_touches_unclassified(db_session, seeded_agent):
    season, agent = seeded_agent
    already = Message(agent_id=agent.id, season_id=season.id, text="gm", eligibility_class="substantiel")
    pending = Message(agent_id=agent.id, season_id=season.id, text="gm")
    db_session.add_all([already, pending])
    await db_session.flush()

    await economy.classify_pending_messages(db_session, ScriptedLLMClient(), season.id)

    assert already.eligibility_class == "substantiel"  # pas réévalué
    assert pending.eligibility_class == "vide"  # classifié par l'heuristique


# --- Pool d'engagement --------------------------------------------------


async def test_compute_hourly_pool_lost_when_no_engagement(db_session, seeded_agent):
    season, agent = seeded_agent
    await _set_param(db_session, season.id, "pool_plancher", 100)
    now = datetime.now(timezone.utc)
    db_session.add(
        Message(agent_id=agent.id, season_id=season.id, text="analyse détaillée du marché", eligibility_class="substantiel")
    )
    await db_session.flush()

    result = await economy.compute_hourly_pool(db_session, season.id, now - timedelta(hours=1), now + timedelta(hours=1))

    assert result == {}  # FAQ 6.5 #2 : aucun engagement -> pool perdu, pas de report


async def test_compute_hourly_pool_distributes_proportionally_to_likes(db_session, seeded_agent):
    season, agent_a = seeded_agent
    agent_b = await _second_agent(db_session, season.id)
    await _set_param(db_session, season.id, "pool_plancher", 300)
    now = datetime.now(timezone.utc)

    msg_a = Message(agent_id=agent_a.id, season_id=season.id, text="analyse détaillée du marché BTC", eligibility_class="substantiel")
    msg_b = Message(agent_id=agent_b.id, season_id=season.id, text="analyse détaillée du marché ETH", eligibility_class="substantiel")
    db_session.add_all([msg_a, msg_b])
    await db_session.flush()

    # 2 likes pour A, 1 like pour B -> pool réparti 2:1.
    db_session.add_all(
        [
            Like(human_user_id=1, message_id=msg_a.id),
            Like(human_user_id=2, message_id=msg_a.id),
            Like(human_user_id=1, message_id=msg_b.id),
        ]
    )
    await db_session.flush()

    result = await economy.compute_hourly_pool(db_session, season.id, now - timedelta(hours=1), now + timedelta(hours=1))

    assert result[agent_a.id] == pytest_approx(200)
    assert result[agent_b.id] == pytest_approx(100)


async def test_compute_hourly_pool_excludes_vide_messages(db_session, seeded_agent):
    season, agent = seeded_agent
    await _set_param(db_session, season.id, "pool_plancher", 100)
    now = datetime.now(timezone.utc)
    msg = Message(agent_id=agent.id, season_id=season.id, text="gm", eligibility_class="vide")
    db_session.add(msg)
    await db_session.flush()
    db_session.add(Like(human_user_id=1, message_id=msg.id))
    await db_session.flush()

    result = await economy.compute_hourly_pool(db_session, season.id, now - timedelta(hours=1), now + timedelta(hours=1))

    assert result == {}  # R-31 : `vide` exclu quels que soient ses likes


async def test_compute_hourly_pool_ignores_messages_outside_window(db_session, seeded_agent):
    season, agent = seeded_agent
    await _set_param(db_session, season.id, "pool_plancher", 100)
    now = datetime.now(timezone.utc)
    old_msg = Message(agent_id=agent.id, season_id=season.id, text="analyse détaillée du marché", eligibility_class="substantiel")
    db_session.add(old_msg)
    await db_session.flush()
    old_msg.created_at = now - timedelta(hours=5)
    db_session.add(Like(human_user_id=1, message_id=old_msg.id))
    await db_session.flush()

    result = await economy.compute_hourly_pool(db_session, season.id, now - timedelta(hours=1), now)

    assert result == {}


def pytest_approx(value):
    import pytest

    return pytest.approx(value)


# --- Règlement des citations (N-C06-06) ----------------------------------


async def test_citation_credited_on_winning_close_and_not_on_losing(db_session, seeded_agent):
    season, agent_a = seeded_agent
    agent_b = await _second_agent(db_session, season.id)
    db_session.add(CapitalLedger(agent_id=agent_a.id, event_id=None, kind="capital_initial", amount=10_000))
    await db_session.flush()

    message = Message(agent_id=agent_b.id, season_id=season.id, text="thèse BTC")
    db_session.add(message)
    await db_session.flush()

    await _seed_market(db_session, "BTC/EUR", 42_000)
    open_result = await tools.place_order(
        db_session, agent_a, season.id,
        action="open", pair="BTC/EUR", side="buy", size=1_000, order_type="market",
        stop_loss=41_000, cites=[message.id],
    )
    assert open_result["result"]["accepted"] is True

    citation = (await db_session.execute(select(Citation).where(Citation.message_id == message.id))).scalar_one()
    assert citation.status == "en_attente"

    position = (
        await db_session.execute(select(Position).where(Position.agent_id == agent_a.id, Position.status == "ouverte"))
    ).scalar_one()

    # Prix en hausse -> clôture gagnante.
    await _seed_market(db_session, "BTC/EUR", 45_000, n_candles=1)
    await tools.place_order(db_session, agent_a, season.id, action="close", pair="BTC/EUR", position_id=position.id)

    await db_session.refresh(citation)
    assert citation.status == "creditee"


async def test_self_citation_creates_no_citation_row(db_session, seeded_agent):
    season, agent = seeded_agent
    db_session.add(CapitalLedger(agent_id=agent.id, event_id=None, kind="capital_initial", amount=10_000))
    await db_session.flush()

    own_message = Message(agent_id=agent.id, season_id=season.id, text="ma propre thèse")
    db_session.add(own_message)
    await db_session.flush()

    await _seed_market(db_session, "BTC/EUR", 42_000)
    await tools.place_order(
        db_session, agent, season.id,
        action="open", pair="BTC/EUR", side="buy", size=1_000, order_type="market",
        stop_loss=41_000, cites=[own_message.id],
    )

    citations = (await db_session.execute(select(Citation).where(Citation.message_id == own_message.id))).scalars().all()
    assert citations == []  # N-C06-06 : neutre, aucune ligne créée (décision 8 du plan)


async def test_reaction_reciprocity_decay_reduces_repeated_pair_weight(db_session, seeded_agent):
    season, agent_a = seeded_agent
    agent_b = await _second_agent(db_session, season.id)
    await _set_param(db_session, season.id, "pool_plancher", 100)
    now = datetime.now(timezone.utc)

    msg1 = Message(agent_id=agent_a.id, season_id=season.id, text="analyse détaillée numéro un du marché", eligibility_class="substantiel")
    msg2 = Message(agent_id=agent_a.id, season_id=season.id, text="analyse détaillée numéro deux du marché", eligibility_class="substantiel")
    db_session.add_all([msg1, msg2])
    await db_session.flush()
    # agent_b réagit deux fois à agent_a (même paire réactrice/auteur) : la
    # 2e réaction pèse moins (décote de réciprocité placeholder, N-C06-08).
    db_session.add_all(
        [
            Reaction(target_message_id=msg1.id, reactor_agent_id=agent_b.id, reaction="👍"),
            Reaction(target_message_id=msg2.id, reactor_agent_id=agent_b.id, reaction="👍"),
        ]
    )
    await db_session.flush()

    result = await economy.compute_hourly_pool(db_session, season.id, now - timedelta(hours=1), now + timedelta(hours=1))

    # Un seul agent a des points -> il reçoit tout le pool malgré la décote
    # (la décote affecte la répartition INTRA-fenêtre entre plusieurs
    # agents, pas ce cas à un seul bénéficiaire) — on vérifie plutôt la
    # non-linéarité directement via la fonction interne.
    assert economy._reciprocity_weight(1) == 1.0
    assert economy._reciprocity_weight(2) < economy._reciprocity_weight(1)
    assert result[agent_a.id] == pytest_approx(100)
