"""Pipeline de validation — ordre exact des codes d'erreur (N-C12-04/14/15).
Chaque test isole UNE cause de rejet en gardant tout le reste valide, pour
vérifier que c'est bien CE code qui sort en premier (N-C12-05).
"""

from app.domain.arena.models import CapitalLedger, Position
from app.domain.arena.orchestrator.validation import validate_order


async def _credit_capital(db, agent_id: str, amount: float) -> None:
    db.add(CapitalLedger(agent_id=agent_id, event_id=None, kind="capital_initial", amount=amount))
    await db.flush()


def _open_payload(**overrides) -> dict:
    payload = {
        "action": "open",
        "pair": "BTC/EUR",
        "side": "buy",
        "size": 1000,
        "order_type": "market",
        "stop_loss": 40000.0,
        "decision_summary": "test",
    }
    payload.update(overrides)
    return payload


async def test_open_accepted_when_everything_valid(db_session, seeded_agent):
    season, agent = seeded_agent
    await _credit_capital(db_session, agent.id, 10_000)

    order = await validate_order(db_session, agent_id=agent.id, season_id=season.id, payload=_open_payload())

    assert order.status == "accepte"
    assert order.rejected_code is None


async def test_kill_switch_when_season_not_active(db_session, seeded_agent):
    season, agent = seeded_agent
    season.state = "en_pause"
    await _credit_capital(db_session, agent.id, 10_000)

    order = await validate_order(db_session, agent_id=agent.id, season_id=season.id, payload=_open_payload())

    assert order.status == "rejete"
    assert order.rejected_code == "E-KILL-SWITCH"


async def test_pair_unknown(db_session, seeded_agent):
    season, agent = seeded_agent
    await _credit_capital(db_session, agent.id, 10_000)

    order = await validate_order(
        db_session, agent_id=agent.id, season_id=season.id, payload=_open_payload(pair="XRP/EUR")
    )

    assert order.rejected_code == "E-PAIR-UNKNOWN"


async def test_no_stop_required_for_open(db_session, seeded_agent):
    season, agent = seeded_agent
    await _credit_capital(db_session, agent.id, 10_000)

    order = await validate_order(
        db_session, agent_id=agent.id, season_id=season.id, payload=_open_payload(stop_loss=None)
    )

    assert order.rejected_code == "E-NO-STOP"


async def test_position_exists_blocks_second_open(db_session, seeded_agent):
    season, agent = seeded_agent
    await _credit_capital(db_session, agent.id, 10_000)
    db_session.add(
        Position(agent_id=agent.id, pair="BTC/EUR", side="buy", size=500, stop_loss=39000.0, status="ouverte")
    )
    await db_session.flush()

    order = await validate_order(db_session, agent_id=agent.id, season_id=season.id, payload=_open_payload())

    assert order.rejected_code == "E-POSITION-EXISTS"


async def test_insufficient_capital(db_session, seeded_agent):
    season, agent = seeded_agent
    await _credit_capital(db_session, agent.id, 100)  # < size demandé (1000)

    order = await validate_order(db_session, agent_id=agent.id, season_id=season.id, payload=_open_payload())

    assert order.rejected_code == "E-INSUFFICIENT-CAPITAL"


async def test_size_exceeded(db_session, seeded_agent):
    season, agent = seeded_agent
    await _credit_capital(db_session, agent.id, 100_000)

    order = await validate_order(
        db_session, agent_id=agent.id, season_id=season.id, payload=_open_payload(size=6_000)
    )

    assert order.rejected_code == "E-SIZE-EXCEEDED"


async def test_modify_stop_widening_rejected(db_session, seeded_agent):
    season, agent = seeded_agent
    await _credit_capital(db_session, agent.id, 10_000)
    position = Position(agent_id=agent.id, pair="BTC/EUR", side="buy", size=500, stop_loss=40000.0, status="ouverte")
    db_session.add(position)
    await db_session.flush()

    order = await validate_order(
        db_session,
        agent_id=agent.id,
        season_id=season.id,
        payload={"action": "modify", "pair": "BTC/EUR", "position_id": position.id, "stop_loss": 39000.0},
    )

    assert order.rejected_code == "E-STOP-WIDENING"


async def test_modify_stop_tightening_accepted(db_session, seeded_agent):
    season, agent = seeded_agent
    await _credit_capital(db_session, agent.id, 10_000)
    position = Position(agent_id=agent.id, pair="BTC/EUR", side="buy", size=500, stop_loss=40000.0, status="ouverte")
    db_session.add(position)
    await db_session.flush()

    order = await validate_order(
        db_session,
        agent_id=agent.id,
        season_id=season.id,
        payload={"action": "modify", "pair": "BTC/EUR", "position_id": position.id, "stop_loss": 41000.0},
    )

    assert order.status == "accepte"


async def test_close_position_unknown(db_session, seeded_agent):
    season, agent = seeded_agent
    await _credit_capital(db_session, agent.id, 10_000)

    order = await validate_order(
        db_session,
        agent_id=agent.id,
        season_id=season.id,
        payload={"action": "close", "pair": "BTC/EUR", "position_id": "does-not-exist"},
    )

    assert order.rejected_code == "E-POSITION-UNKNOWN"
