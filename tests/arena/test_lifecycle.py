"""Cycle de vie (chapitre 5) — mort, phase funéraire, testament,
renaissance. Les délais (`duree_max_funeraire`, `delai_renaissance`) sont
vérifiés en manipulant les timestamps plutôt qu'en attendant réellement
(voir plan C2, section Vérification)."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.domain.arena.agents import tools
from app.domain.arena.models import Agent, CapitalLedger, EventRecord, SeasonParam, Testament, TokenLedger
from app.domain.arena.orchestrator import lifecycle


async def _set_param(db, season_id: str, name: str, value) -> None:
    row = await db.get(SeasonParam, {"season_id": season_id, "name": name})
    if row is None:
        db.add(SeasonParam(season_id=season_id, name=name, value=value, visibility="public"))
    else:
        row.value = value
    await db.flush()


async def test_check_death_enters_funeral_and_credits_allocation(db_session, seeded_agent):
    season, agent = seeded_agent
    await _set_param(db_session, season.id, "allocation_funeraire", 500)
    # Pas de CapitalLedger crédité -> capital == 0 == seuil_mort par défaut.

    died = await lifecycle.check_death(db_session, agent)

    assert died is True
    assert agent.status == "funeraire"
    assert agent.died_at is not None

    death_events = (
        await db_session.execute(select(EventRecord).where(EventRecord.type == "agent.death"))
    ).scalars().all()
    assert len(death_events) == 1

    balance_rows = (
        await db_session.execute(select(TokenLedger.amount).where(TokenLedger.agent_id == agent.id))
    ).scalars().all()
    assert float(sum(balance_rows)) == 500


async def test_check_death_is_idempotent(db_session, seeded_agent):
    season, agent = seeded_agent
    await lifecycle.check_death(db_session, agent)
    first_died_at = agent.died_at

    died_again = await lifecycle.check_death(db_session, agent)

    assert died_again is False
    assert agent.died_at == first_died_at  # pas réémis, pas rebasculé


async def test_write_testament_requires_funeral_status(db_session, seeded_agent):
    _season, agent = seeded_agent
    assert agent.status == "actif"

    result = await tools.write_testament(db_session, agent, content="trop tôt")

    assert result["status"] == "error"
    assert result["error_code"] == "E-NOT-DYING"


async def test_write_testament_seals_content_without_ending_funeral(db_session, seeded_agent):
    season, agent = seeded_agent
    await _set_param(db_session, season.id, "taille_max_testament", 2_000)
    await lifecycle.check_death(db_session, agent)
    assert agent.status == "funeraire"

    result = await tools.write_testament(db_session, agent, content="Ne repositionnez jamais tout le capital d'un coup.")

    assert result["status"] == "ok"
    assert agent.status == "funeraire"  # scellé, mais la phase funéraire continue (décision d'implémentation)

    testament = (await db_session.execute(select(Testament).where(Testament.agent_id == agent.id))).scalar_one()
    assert testament.state == "scelle"
    assert "capital d'un coup" in testament.content


async def test_write_testament_twice_gives_already_sealed(db_session, seeded_agent):
    _season, agent = seeded_agent
    await lifecycle.check_death(db_session, agent)
    await tools.write_testament(db_session, agent, content="premier testament")

    result = await tools.write_testament(db_session, agent, content="je change d'avis")

    assert result["status"] == "error"
    assert result["error_code"] == "E-ALREADY-SEALED"
    testament = (await db_session.execute(select(Testament).where(Testament.agent_id == agent.id))).scalar_one()
    assert testament.content == "premier testament"  # pas réécrit


async def test_taille_max_testament_truncates_content(db_session, seeded_agent):
    season, agent = seeded_agent
    await _set_param(db_session, season.id, "taille_max_testament", 10)
    await lifecycle.check_death(db_session, agent)

    await tools.write_testament(db_session, agent, content="beaucoup plus long que dix caractères")

    testament = (await db_session.execute(select(Testament).where(Testament.agent_id == agent.id))).scalar_one()
    assert len(testament.content) == 10


async def test_check_funeral_expirations_ends_funeral_with_empty_testament_if_never_written(db_session, seeded_agent):
    season, agent = seeded_agent
    await _set_param(db_session, season.id, "duree_max_funeraire", 1)  # 1 seconde
    await lifecycle.check_death(db_session, agent)
    agent.died_at = datetime.now(timezone.utc) - timedelta(seconds=5)
    await db_session.flush()

    await lifecycle.check_funeral_expirations(db_session, season.id)
    await db_session.refresh(agent)

    assert agent.status == "mort"
    testament = (await db_session.execute(select(Testament).where(Testament.agent_id == agent.id))).scalar_one()
    assert testament.state == "scelle"
    assert testament.content == ""  # documenté comme une issue possible, N-C05-06


async def test_check_funeral_expirations_ends_funeral_after_early_write(db_session, seeded_agent):
    season, agent = seeded_agent
    await _set_param(db_session, season.id, "duree_max_funeraire", 1)
    await lifecycle.check_death(db_session, agent)
    await tools.write_testament(db_session, agent, content="mes leçons")
    agent.died_at = datetime.now(timezone.utc) - timedelta(seconds=5)
    await db_session.flush()

    await lifecycle.check_funeral_expirations(db_session, season.id)
    await db_session.refresh(agent)

    assert agent.status == "mort"
    testament = (await db_session.execute(select(Testament).where(Testament.agent_id == agent.id))).scalar_one()
    assert testament.content == "mes leçons"  # pas écrasé par la fin de phase


async def test_process_rebirths_creates_next_generation_with_inheritance(db_session, seeded_agent):
    season, agent = seeded_agent
    dynasty_id = agent.dynasty_id
    await _set_param(db_session, season.id, "delai_renaissance", 0)
    await _set_param(db_session, season.id, "capital_initial", 10_000)
    await _set_param(db_session, season.id, "allocation_horaire_par_modele", 50_000)

    await lifecycle.check_death(db_session, agent)
    await tools.write_testament(db_session, agent, content="J'ai ouvert trop de positions à la fois.")
    await lifecycle.end_funeral(db_session, agent)
    assert agent.status == "mort"

    await lifecycle.process_rebirths(db_session, season.id)

    successor = (
        await db_session.execute(
            select(Agent).where(Agent.dynasty_id == dynasty_id, Agent.generation == agent.generation + 1)
        )
    ).scalar_one()
    assert successor.status == "actif"
    assert successor.personality_id == agent.personality_id  # Q-11 non tranchée, continuité par défaut

    capital_rows = (
        await db_session.execute(select(CapitalLedger.amount).where(CapitalLedger.agent_id == successor.id))
    ).scalars().all()
    assert float(sum(capital_rows)) == 10_000

    token_rows = (
        await db_session.execute(select(TokenLedger.amount).where(TokenLedger.agent_id == successor.id))
    ).scalars().all()
    assert float(sum(token_rows)) == 50_000  # allocation initiale immédiate, N-C12-13

    birth_events = (await db_session.execute(select(EventRecord).where(EventRecord.type == "agent.birth"))).scalars().all()
    assert len(birth_events) == 1

    testaments = await lifecycle.lineage_testaments(db_session, dynasty_id)
    assert len(testaments) == 1
    assert testaments[0]["content"] == "J'ai ouvert trop de positions à la fois."


async def test_process_rebirths_waits_for_delai(db_session, seeded_agent):
    season, agent = seeded_agent
    await _set_param(db_session, season.id, "delai_renaissance", 3_600)
    await lifecycle.check_death(db_session, agent)
    await lifecycle.end_funeral(db_session, agent)

    await lifecycle.process_rebirths(db_session, season.id)

    successor_count = (
        await db_session.execute(
            select(Agent.id).where(Agent.dynasty_id == agent.dynasty_id, Agent.generation == agent.generation + 1)
        )
    ).first()
    assert successor_count is None  # délai pas encore écoulé


async def test_process_rebirths_does_not_duplicate(db_session, seeded_agent):
    season, agent = seeded_agent
    await _set_param(db_session, season.id, "delai_renaissance", 0)
    await lifecycle.check_death(db_session, agent)
    await lifecycle.end_funeral(db_session, agent)

    await lifecycle.process_rebirths(db_session, season.id)
    await lifecycle.process_rebirths(db_session, season.id)  # rejoué (H+0 suivant)

    successors = (
        await db_session.execute(
            select(Agent.id).where(Agent.dynasty_id == agent.dynasty_id, Agent.generation == agent.generation + 1)
        )
    ).scalars().all()
    assert len(successors) == 1
