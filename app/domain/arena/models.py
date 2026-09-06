"""Modèles de l'arène (couche C1, Livre chapitre 15 — base de données).

Fichier nouveau sous `app/domain/arena/` (AMEND-04) — pas
`app/domain/models.py` lui-même, qui se contente d'importer ce module pour
enregistrer ces tables sur `Base.metadata` (dev `create_all`, app/core/main.py).

Principes verrouillés du chapitre 15, respectés partout ici :
- `events` = source de vérité unique, append-only (N-C15-01) ; toute autre
  table est une projection reconstructible.
- Soldes en ledger append-only (somme des écritures), jamais de colonne
  `balance` mutable (N-C15-02).
- Colonnes `payload`/`value` en `JSON` portable (pas `JSONB` Postgres) pour
  que la suite de tests tourne sur SQLite sans Docker/Postgres — la prod
  reste Postgres (AMEND-03), `JSON` y est simplement stocké en `json`/`jsonb`
  selon la version, aucune perte de fonctionnalité pour nos usages (lecture
  intégrale du payload, jamais de requête sur une clé interne au JSON).

Portée C1 (voir le plan) : pas de `testaments`/`memories` — la mort/mémoire
sont hors DoD C1, ajoutées naturellement en C2 sans reprise de schéma (les
types d'événements `agent.death`/`agent.birth` existent déjà dans l'Annexe
B, juste pas produits par le code de cette passe).
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Season(Base):
    __tablename__ = "arena_seasons"

    id = Column(String(36), primary_key=True, default=_uuid)
    state = Column(String, nullable=False, default="configuration")
    mode = Column(String, nullable=False, default="perpetuelle")
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "state IN ('configuration','active','en_pause','fin_annoncee','terminee','archivee')",
            name="ck_arena_seasons_state",
        ),
        CheckConstraint("mode IN ('datee','perpetuelle')", name="ck_arena_seasons_mode"),
    )


class SeasonParam(Base):
    """Registre des paramètres (Annexe E) — clé (season_id, name)."""

    __tablename__ = "arena_season_params"

    season_id = Column(String(36), ForeignKey("arena_seasons.id"), primary_key=True)
    name = Column(String, primary_key=True)
    value = Column(JSON, nullable=False)
    visibility = Column(String, nullable=False, default="public")
    modifiable_en_saison = Column(String, nullable=False, default="non")
    owner_chapter = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("visibility IN ('public','secret')", name="ck_season_params_visibility"),
        CheckConstraint(
            "modifiable_en_saison IN ('oui','non','urgence_journalisee')",
            name="ck_season_params_modifiable",
        ),
    )


class Dynasty(Base):
    __tablename__ = "arena_dynasties"

    id = Column(String(36), primary_key=True, default=_uuid)
    season_id = Column(String(36), ForeignKey("arena_seasons.id"), nullable=False)
    name = Column(String, nullable=False)
    model = Column(String, nullable=False)
    color = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("season_id", "name", name="uq_dynasty_name_per_season"),)


class Agent(Base):
    __tablename__ = "arena_agents"

    id = Column(String(36), primary_key=True, default=_uuid)
    dynasty_id = Column(String(36), ForeignKey("arena_dynasties.id"), nullable=False)
    generation = Column(Integer, nullable=False, default=1)
    personality_id = Column(String, nullable=True)
    # C1 : machine à états restreinte à {actif, veille_budget, veille_saison}
    # (funeraire/mort hors DoD C1, décision de portée 7 du plan) — la
    # contrainte reste ouverte aux 5 valeurs du Livre pour ne pas re-migrer
    # en C2.
    status = Column(String, nullable=False, default="actif")
    born_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    died_at = Column(DateTime(timezone=True), nullable=True)
    # Curseur de lecture d'inbox (R-53 : "dépile non-lus, coût proportionnel
    # au volume lu") — pas dans le Livre au niveau schéma, nécessaire pour
    # implémenter le comportement décrit sans re-imputer deux fois le même
    # événement.
    inbox_read_until = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("dynasty_id", "generation", name="uq_agent_generation_per_dynasty"),
        CheckConstraint(
            "status IN ('actif','veille_budget','veille_saison','funeraire','mort')",
            name="ck_agent_status",
        ),
    )


class EventRecord(Base):
    """`events` — source de vérité unique (N-C15-01). Append-only par
    convention applicative (aucun UPDATE/DELETE émis par ce code)."""

    __tablename__ = "arena_events"

    id = Column(String(36), primary_key=True, default=_uuid)
    # 13 types (Annexe B.1, AMEND-14 : `no_trade.logged` ajouté) — validé
    # côté schéma Pydantic (events.py), pas par une CHECK SQL ici (portable
    # SQLite/Postgres sans dupliquer la liste dans une contrainte).
    type = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    season_id = Column(String(36), ForeignKey("arena_seasons.id"), nullable=False)
    sender = Column(String, nullable=False)  # agent_id | 'orchestrator' | 'system'
    recipient = Column(String(36), nullable=True)  # AMEND-13 ; NULL = public
    payload = Column(JSON, nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_arena_events_type_timestamp", "type", "timestamp"),
        Index(
            "ix_arena_events_recipient",
            "recipient",
            sqlite_where=recipient.isnot(None),
            postgresql_where=recipient.isnot(None),
        ),
    )


class TokenLedger(Base):
    __tablename__ = "arena_token_ledger"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(36), ForeignKey("arena_agents.id"), nullable=False)
    # Nullable : une imputation d'outil/LLM (N-C16-03) n'a pas d'événement
    # Annexe B associé — seules les allocations (tokens.allocation) en ont.
    event_id = Column(String(36), ForeignKey("arena_events.id"), nullable=True)
    kind = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)  # signé : + crédit, - imputation
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "kind IN ('allocation_base','allocation_pool','allocation_funeraire',"
            "'imputation_outil','imputation_llm','decouvert')",
            name="ck_token_ledger_kind",
        ),
    )


class CapitalLedger(Base):
    __tablename__ = "arena_capital_ledger"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(36), ForeignKey("arena_agents.id"), nullable=False)
    # Nullable : `capital_initial` (financement à la naissance) et les
    # écritures `frais` n'ont pas d'événement Annexe B dédié — seul
    # `pnl_realise` en a un naturellement (trade.closed), mais on garde la
    # même règle que TokenLedger pour rester simple et cohérent.
    event_id = Column(String(36), ForeignKey("arena_events.id"), nullable=True)
    kind = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)  # signé
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "kind IN ('capital_initial','pnl_realise','frais')",
            name="ck_capital_ledger_kind",
        ),
    )


class Order(Base):
    __tablename__ = "arena_orders"

    id = Column(String(36), primary_key=True, default=_uuid)
    agent_id = Column(String(36), ForeignKey("arena_agents.id"), nullable=False)
    season_id = Column(String(36), ForeignKey("arena_seasons.id"), nullable=False)
    action = Column(String, nullable=False)
    pair = Column(String, nullable=False)
    side = Column(String, nullable=True)  # requis pour action=open
    size = Column(Numeric, nullable=True)
    order_type = Column(String, nullable=True)  # market | limit, requis pour open
    limit_price = Column(Numeric, nullable=True)
    stop_loss = Column(Numeric, nullable=True)
    take_profit = Column(Numeric, nullable=True)
    decision_summary = Column(Text, nullable=True)
    cites = Column(JSON, nullable=True)  # message_id[] — chat hors C1, réservé
    position_id = Column(String(36), ForeignKey("arena_positions.id"), nullable=True)
    status = Column(String, nullable=False, default="soumis")
    rejected_code = Column(String, nullable=True)
    # AMEND-14 (décision 9 du plan) : informatif uniquement, ne bloque jamais.
    declared_risk_pct = Column(Numeric, nullable=True)
    risk_calculated_pct = Column(Numeric, nullable=True)
    strategy_ref = Column(String, nullable=True)  # passthrough non validé en C1
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("action IN ('open','modify','close')", name="ck_order_action"),
        CheckConstraint("side IN ('buy','sell') OR side IS NULL", name="ck_order_side"),
        CheckConstraint(
            "order_type IN ('market','limit') OR order_type IS NULL", name="ck_order_type"
        ),
        CheckConstraint(
            "status IN ('soumis','accepte','en_attente','execute','rejete','expire','annule')",
            name="ck_order_status",
        ),
    )


class Position(Base):
    __tablename__ = "arena_positions"

    id = Column(String(36), primary_key=True, default=_uuid)
    agent_id = Column(String(36), ForeignKey("arena_agents.id"), nullable=False)
    pair = Column(String, nullable=False)
    side = Column(String, nullable=False)
    size = Column(Numeric, nullable=False)
    stop_loss = Column(Numeric, nullable=False)  # R-41 : obligatoire
    take_profit = Column(Numeric, nullable=True)
    status = Column(String, nullable=False, default="ouverte")
    close_reason = Column(String, nullable=True)
    pnl = Column(Numeric, nullable=True)
    opened_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("side IN ('buy','sell')", name="ck_position_side"),
        CheckConstraint("status IN ('ouverte','fermee')", name="ck_position_status"),
        CheckConstraint(
            "close_reason IN ('stop','take_profit','agent_close','season_end') "
            "OR close_reason IS NULL",
            name="ck_position_close_reason",
        ),
        # N-C07-05 : une seule position ouverte par (agent, paire).
        Index(
            "uq_position_open_per_agent_pair",
            "agent_id",
            "pair",
            unique=True,
            sqlite_where=status == "ouverte",
            postgresql_where=status == "ouverte",
        ),
    )


class Fill(Base):
    __tablename__ = "arena_fills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Nullable : un fill déclenché par le moteur de surveillance (stop/TP,
    # N-C13-02) n'a pas d'`Order` d'origine — personne ne l'a soumis.
    order_id = Column(String(36), ForeignKey("arena_orders.id"), nullable=True)
    position_id = Column(String(36), ForeignKey("arena_positions.id"), nullable=False)
    fill_price = Column(Numeric, nullable=False)
    fees = Column(Numeric, nullable=False)
    slippage = Column(Numeric, nullable=False)
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Message(Base):
    """Chat console minimal (C1 : un seul agent, pas de conversation réelle
    — sert surtout à ce que `post_message` ait un effet observable et
    testable ; le vrai chat multi-agents/public est C2+, chapitre 8)."""

    __tablename__ = "arena_messages"

    id = Column(String(36), primary_key=True, default=_uuid)
    season_id = Column(String(36), ForeignKey("arena_seasons.id"), nullable=False)
    sender = Column(String, nullable=False)  # agent_id | 'orchestrator'
    content = Column(Text, nullable=False)
    cites = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MarketCandle(Base):
    """OHLCV 1 minute (N-C14-02) — seule granularité capturée ; les
    timeframes supérieurs sont agrégés à la demande, jamais stockés."""

    __tablename__ = "arena_market_candles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pair = Column(String, nullable=False)
    candle_time = Column(DateTime(timezone=True), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("pair", "candle_time", name="uq_candle_pair_time"),
        Index("ix_candle_pair_time", "pair", "candle_time"),
    )


class OrderbookSnapshot(Base):
    """Instantané de carnet (N-C14-03) — top-of-book seulement (bid/ask),
    suffisant pour `ref`/`half_spread` du modèle de fill (Annexe F)."""

    __tablename__ = "arena_orderbook_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pair = Column(String, nullable=False)
    bid = Column(Float, nullable=False)
    ask = Column(Float, nullable=False)
    captured_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (Index("ix_orderbook_pair_time", "pair", "captured_at"),)


class ArenaLog(Base):
    """Journal opérationnel (pas un type Annexe B — diagnostics internes :
    erreurs de capture, exceptions rattrapées dans le worker/la boucle
    agent). Distinct de `arena_events` (source de vérité du jeu, chapitre
    15) : ceci sert l'observabilité admin, jamais lu par les agents ni le
    public. Append-only comme le reste."""

    __tablename__ = "arena_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    level = Column(String, nullable=False)
    component = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)

    __table_args__ = (
        CheckConstraint("level IN ('info','warning','error')", name="ck_arena_logs_level"),
        Index("ix_arena_logs_created_at", "created_at"),
    )
