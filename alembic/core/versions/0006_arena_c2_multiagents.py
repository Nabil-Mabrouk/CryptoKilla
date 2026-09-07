"""arena: C2 multi-agents et économie (testaments, mémoire, réactions,
citations, profils humains, likes) + migration du DDL `arena_messages`

Revision ID: 0006_arena_c2
Revises: 0005_arena_logs
Create Date: 2026-09-06

Écrite à la main (même raison que 0004 : la chaîne `core` n'importe pas
`app.domain.arena.models`, pas d'autogenerate possible). Reflète
exactement `app/domain/arena/models.py` après la passe C2 (chapitre 34) ;
toute divergence future doit être corrigée dans les deux à la fois.

`arena_messages` passe du DDL provisoire C1 (`sender` texte libre,
`content`) au DDL exact du Livre (`agent_id` FK non-null, `text`,
`attachments`/`mentions`/`eligibility_class`) — chapitre 15, chapitre 18.
Migration de données incluse (backfill `agent_id`/`text` depuis
`sender`/`content`) au cas où des lignes existeraient déjà (le seul
outil qui écrivait dans cette table en C1, `post_message`, y stockait
toujours `sender=agent.id`) — prudence de production, pas une hypothèse
sur l'état réel d'un environnement donné.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_arena_c2"
down_revision: Union[str, None] = "0005_arena_logs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Migration du DDL `arena_messages` (C1 provisoire -> Livre) --------
    op.add_column("arena_messages", sa.Column("agent_id", sa.String(36), nullable=True))
    op.add_column("arena_messages", sa.Column("text", sa.Text(), nullable=True))
    op.add_column("arena_messages", sa.Column("attachments", sa.JSON(), nullable=True))
    op.add_column("arena_messages", sa.Column("mentions", sa.JSON(), nullable=True))
    op.add_column("arena_messages", sa.Column("eligibility_class", sa.String(), nullable=True))

    op.execute("UPDATE arena_messages SET agent_id = sender, text = content")
    op.execute("UPDATE arena_messages SET attachments = '[]' WHERE attachments IS NULL")
    op.execute("UPDATE arena_messages SET mentions = '[]' WHERE mentions IS NULL")
    op.execute("UPDATE arena_messages SET cites = '[]' WHERE cites IS NULL")

    with op.batch_alter_table("arena_messages") as batch_op:
        batch_op.alter_column("agent_id", nullable=False)
        batch_op.alter_column("text", nullable=False)
        batch_op.alter_column("attachments", nullable=False)
        batch_op.alter_column("mentions", nullable=False)
        batch_op.alter_column("cites", nullable=False)
        batch_op.drop_column("sender")
        batch_op.drop_column("content")
        batch_op.create_foreign_key(
            "fk_arena_messages_agent_id", "arena_agents", ["agent_id"], ["id"]
        )
        batch_op.create_check_constraint(
            "ck_message_eligibility",
            "eligibility_class IN ('substantiel','contextuel','vide') OR eligibility_class IS NULL",
        )
    op.create_index("ix_arena_messages_season_created", "arena_messages", ["season_id", "created_at"])

    # --- Nouvelles tables C2 -------------------------------------------------
    op.create_table(
        "arena_reactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("target_message_id", sa.String(36), sa.ForeignKey("arena_messages.id"), nullable=False),
        sa.Column("reactor_agent_id", sa.String(36), sa.ForeignKey("arena_agents.id"), nullable=False),
        sa.Column("reaction", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_arena_reactions_pair", "arena_reactions", ["reactor_agent_id", "target_message_id"])

    op.create_table(
        "arena_citations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("message_id", sa.String(36), sa.ForeignKey("arena_messages.id"), nullable=False),
        sa.Column("order_id", sa.String(36), sa.ForeignKey("arena_orders.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.CheckConstraint("status IN ('en_attente','creditee','non_creditee')", name="ck_citation_status"),
    )

    op.create_table(
        "arena_memories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("arena_agents.id"), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("type IN ('episodic','semantic','procedural')", name="ck_memory_type"),
    )
    op.create_index("ix_arena_memories_agent_type", "arena_memories", ["agent_id", "type"])

    op.create_table(
        "arena_human_profiles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("anonymized_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "arena_likes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("human_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("message_id", sa.String(36), sa.ForeignKey("arena_messages.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("human_user_id", "message_id", name="uq_like_per_human_message"),
    )

    op.create_table(
        "arena_testaments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("arena_agents.id"), nullable=False, unique=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("sealed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("state IN ('en_redaction','scelle','publie')", name="ck_testament_state"),
    )


def downgrade() -> None:
    op.drop_table("arena_testaments")
    op.drop_table("arena_likes")
    op.drop_table("arena_human_profiles")
    op.drop_index("ix_arena_memories_agent_type", table_name="arena_memories")
    op.drop_table("arena_memories")
    op.drop_table("arena_citations")
    op.drop_index("ix_arena_reactions_pair", table_name="arena_reactions")
    op.drop_table("arena_reactions")

    op.drop_index("ix_arena_messages_season_created", table_name="arena_messages")
    with op.batch_alter_table("arena_messages") as batch_op:
        batch_op.drop_constraint("ck_message_eligibility", type_="check")
        batch_op.drop_constraint("fk_arena_messages_agent_id", type_="foreignkey")
        batch_op.add_column(sa.Column("sender", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("content", sa.Text(), nullable=True))

    op.execute("UPDATE arena_messages SET sender = agent_id, content = text")

    with op.batch_alter_table("arena_messages") as batch_op:
        batch_op.alter_column("sender", nullable=False)
        batch_op.alter_column("content", nullable=False)
        batch_op.alter_column("cites", nullable=True)
        batch_op.drop_column("eligibility_class")
        batch_op.drop_column("mentions")
        batch_op.drop_column("attachments")
        batch_op.drop_column("text")
        batch_op.drop_column("agent_id")
