"""arena: C1 foundation tables (event store, capture, orders, ledgers)

Revision ID: 0004_arena_c1
Revises: 0003_core_user_invite_token
Create Date: 2026-09-01

Écrite à la main (pas `--autogenerate`) : la chaîne `core`
(`alembic/core/env.py`) n'importe aujourd'hui que `app.core.models`, pas
`app.domain.models` — l'autogenerate ne verrait donc pas
`app.domain.arena.models`. Cette migration reflète exactement ce fichier ;
toute divergence future doit être corrigée dans les deux à la fois.

Couche C1 (Livre, chapitre 34) — event-sourcing (chapitre 15), un seul
agent. Pas de `testaments`/`memories` (hors DoD C1, chapitre 34).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_arena_c1"
down_revision: Union[str, None] = "0003_core_user_invite_token"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "arena_seasons",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "state IN ('configuration','active','en_pause','fin_annoncee','terminee','archivee')",
            name="ck_arena_seasons_state",
        ),
        sa.CheckConstraint("mode IN ('datee','perpetuelle')", name="ck_arena_seasons_mode"),
    )

    op.create_table(
        "arena_season_params",
        sa.Column("season_id", sa.String(36), sa.ForeignKey("arena_seasons.id"), primary_key=True),
        sa.Column("name", sa.String(), primary_key=True),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("visibility", sa.String(), nullable=False),
        sa.Column("modifiable_en_saison", sa.String(), nullable=False),
        sa.Column("owner_chapter", sa.String(), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("visibility IN ('public','secret')", name="ck_season_params_visibility"),
        sa.CheckConstraint(
            "modifiable_en_saison IN ('oui','non','urgence_journalisee')",
            name="ck_season_params_modifiable",
        ),
    )

    op.create_table(
        "arena_dynasties",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("season_id", sa.String(36), sa.ForeignKey("arena_seasons.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("color", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("season_id", "name", name="uq_dynasty_name_per_season"),
    )

    op.create_table(
        "arena_agents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("dynasty_id", sa.String(36), sa.ForeignKey("arena_dynasties.id"), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("personality_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("born_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("died_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("inbox_read_until", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("dynasty_id", "generation", name="uq_agent_generation_per_dynasty"),
        sa.CheckConstraint(
            "status IN ('actif','veille_budget','veille_saison','funeraire','mort')",
            name="ck_agent_status",
        ),
    )

    op.create_table(
        "arena_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("season_id", sa.String(36), sa.ForeignKey("arena_seasons.id"), nullable=False),
        sa.Column("sender", sa.String(), nullable=False),
        sa.Column("recipient", sa.String(36), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_arena_events_type_timestamp", "arena_events", ["type", "timestamp"])
    op.create_index(
        "ix_arena_events_recipient",
        "arena_events",
        ["recipient"],
        postgresql_where=sa.text("recipient IS NOT NULL"),
    )

    op.create_table(
        "arena_token_ledger",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("arena_agents.id"), nullable=False),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("arena_events.id"), nullable=True),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("amount", sa.Numeric(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "kind IN ('allocation_base','allocation_pool','allocation_funeraire',"
            "'imputation_outil','imputation_llm','decouvert')",
            name="ck_token_ledger_kind",
        ),
    )

    op.create_table(
        "arena_capital_ledger",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("arena_agents.id"), nullable=False),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("arena_events.id"), nullable=True),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("amount", sa.Numeric(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "kind IN ('capital_initial','pnl_realise','frais')", name="ck_capital_ledger_kind"
        ),
    )

    op.create_table(
        "arena_positions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("arena_agents.id"), nullable=False),
        sa.Column("pair", sa.String(), nullable=False),
        sa.Column("side", sa.String(), nullable=False),
        sa.Column("size", sa.Numeric(), nullable=False),
        sa.Column("stop_loss", sa.Numeric(), nullable=False),
        sa.Column("take_profit", sa.Numeric(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("close_reason", sa.String(), nullable=True),
        sa.Column("pnl", sa.Numeric(), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("side IN ('buy','sell')", name="ck_position_side"),
        sa.CheckConstraint("status IN ('ouverte','fermee')", name="ck_position_status"),
        sa.CheckConstraint(
            "close_reason IN ('stop','take_profit','agent_close','season_end') OR close_reason IS NULL",
            name="ck_position_close_reason",
        ),
    )
    op.create_index(
        "uq_position_open_per_agent_pair",
        "arena_positions",
        ["agent_id", "pair"],
        unique=True,
        postgresql_where=sa.text("status = 'ouverte'"),
    )

    op.create_table(
        "arena_orders",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("arena_agents.id"), nullable=False),
        sa.Column("season_id", sa.String(36), sa.ForeignKey("arena_seasons.id"), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("pair", sa.String(), nullable=False),
        sa.Column("side", sa.String(), nullable=True),
        sa.Column("size", sa.Numeric(), nullable=True),
        sa.Column("order_type", sa.String(), nullable=True),
        sa.Column("limit_price", sa.Numeric(), nullable=True),
        sa.Column("stop_loss", sa.Numeric(), nullable=True),
        sa.Column("take_profit", sa.Numeric(), nullable=True),
        sa.Column("decision_summary", sa.Text(), nullable=True),
        sa.Column("cites", sa.JSON(), nullable=True),
        sa.Column("position_id", sa.String(36), sa.ForeignKey("arena_positions.id"), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("rejected_code", sa.String(), nullable=True),
        sa.Column("declared_risk_pct", sa.Numeric(), nullable=True),
        sa.Column("risk_calculated_pct", sa.Numeric(), nullable=True),
        sa.Column("strategy_ref", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("action IN ('open','modify','close')", name="ck_order_action"),
        sa.CheckConstraint("side IN ('buy','sell') OR side IS NULL", name="ck_order_side"),
        sa.CheckConstraint(
            "order_type IN ('market','limit') OR order_type IS NULL", name="ck_order_type"
        ),
        sa.CheckConstraint(
            "status IN ('soumis','accepte','en_attente','execute','rejete','expire','annule')",
            name="ck_order_status",
        ),
    )

    op.create_table(
        "arena_fills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.String(36), sa.ForeignKey("arena_orders.id"), nullable=False),
        sa.Column("position_id", sa.String(36), sa.ForeignKey("arena_positions.id"), nullable=False),
        sa.Column("fill_price", sa.Numeric(), nullable=False),
        sa.Column("fees", sa.Numeric(), nullable=False),
        sa.Column("slippage", sa.Numeric(), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "arena_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("season_id", sa.String(36), sa.ForeignKey("arena_seasons.id"), nullable=False),
        sa.Column("sender", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("cites", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "arena_market_candles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("pair", sa.String(), nullable=False),
        sa.Column("candle_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("pair", "candle_time", name="uq_candle_pair_time"),
    )
    op.create_index("ix_candle_pair_time", "arena_market_candles", ["pair", "candle_time"])

    op.create_table(
        "arena_orderbook_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("pair", sa.String(), nullable=False),
        sa.Column("bid", sa.Float(), nullable=False),
        sa.Column("ask", sa.Float(), nullable=False),
        sa.Column(
            "captured_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_orderbook_pair_time", "arena_orderbook_snapshots", ["pair", "captured_at"])


def downgrade() -> None:
    op.drop_table("arena_orderbook_snapshots")
    op.drop_table("arena_market_candles")
    op.drop_table("arena_messages")
    op.drop_table("arena_fills")
    op.drop_table("arena_orders")
    op.drop_index("uq_position_open_per_agent_pair", table_name="arena_positions")
    op.drop_table("arena_positions")
    op.drop_table("arena_capital_ledger")
    op.drop_table("arena_token_ledger")
    op.drop_index("ix_arena_events_recipient", table_name="arena_events")
    op.drop_index("ix_arena_events_type_timestamp", table_name="arena_events")
    op.drop_table("arena_events")
    op.drop_table("arena_agents")
    op.drop_table("arena_dynasties")
    op.drop_table("arena_season_params")
    op.drop_table("arena_seasons")
