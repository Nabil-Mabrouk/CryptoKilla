"""Lecture publique de l'arène (`app/domain/routers.py`, section
"Lecture publique") — en particulier `recent_events`, l'historique public
mort/renaissance (Annexe B.1/B.2, types `agent.death`/`agent.birth`).
Vérifie surtout ce que le Livre interdit : aucun contenu de testament
(N-C21-04) et aucun `season_params` secret (ARENA.md §3) ne doit y
transiter."""

from app.domain.arena.agents import tools
from app.domain.arena.models import SeasonParam
from app.domain.arena.orchestrator import lifecycle
from app.domain.routers import _public_life_events


async def _set_param(db, season_id: str, name: str, value) -> None:
    row = await db.get(SeasonParam, {"season_id": season_id, "name": name})
    if row is None:
        db.add(SeasonParam(season_id=season_id, name=name, value=value, visibility="public"))
    else:
        row.value = value
    await db.flush()


async def test_public_life_events_empty_season_returns_empty_list(db_session, seeded_agent):
    season, _agent = seeded_agent

    events = await _public_life_events(db_session, season.id)

    assert events == []


async def test_public_life_events_reports_death_with_final_stats_never_testament(db_session, seeded_agent):
    season, agent = seeded_agent
    await _set_param(db_session, season.id, "allocation_funeraire", 0)

    await lifecycle.check_death(db_session, agent)
    await tools.write_testament(db_session, agent, content="Contenu confidentiel du testament — jamais public ici.")
    await lifecycle.end_funeral(db_session, agent)
    assert agent.status == "mort"

    events = await _public_life_events(db_session, season.id)

    assert len(events) == 1
    event = events[0]
    assert event["type"] == "death"
    assert event["dynasty"] == "test-dynasty"
    assert event["generation"] == 1
    assert event["final_stats"]["nb_trades"] == 0
    # N-C21-04 : un `agent.death` public ne porte jamais le contenu du testament.
    assert "testament" not in str(event).lower()
    assert "confidentiel" not in str(event).lower()


async def test_public_life_events_reports_birth_after_rebirth(db_session, seeded_agent):
    season, agent = seeded_agent
    dynasty_id = agent.dynasty_id
    await _set_param(db_session, season.id, "delai_renaissance", 0)
    await _set_param(db_session, season.id, "capital_initial", 1_000)
    await _set_param(db_session, season.id, "allocation_horaire_par_modele", 0)

    await lifecycle.check_death(db_session, agent)
    await lifecycle.end_funeral(db_session, agent)
    await lifecycle.process_rebirths(db_session, season.id)

    events = await _public_life_events(db_session, season.id)

    kinds = {e["type"] for e in events}
    assert kinds == {"death", "birth"}
    birth = next(e for e in events if e["type"] == "birth")
    assert birth["dynasty"] == "test-dynasty"
    assert birth["generation"] == 2
    assert birth.get("final_stats") is None
    # Aucune donnée `season_params` secrète ne doit fuiter dans un événement public.
    assert dynasty_id  # sanity : la lignée a bien continué, pas une dynastie fantôme
