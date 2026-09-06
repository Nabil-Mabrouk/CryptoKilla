"""arena: operational log table (admin observability)

Revision ID: 0005_arena_logs
Revises: 0004_arena_c1
Create Date: 2026-09-02

Journal opérationnel distinct de `arena_events` (source de vérité du jeu,
Annexe B) — diagnostics internes (erreurs de capture, cycles échoués)
visibles depuis la console admin (voir app/domain/arena/log.py).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_arena_logs"
down_revision: Union[str, None] = "0004_arena_c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "arena_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("level", sa.String(), nullable=False),
        sa.Column("component", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.CheckConstraint("level IN ('info','warning','error')", name="ck_arena_logs_level"),
    )
    op.create_index("ix_arena_logs_created_at", "arena_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_arena_logs_created_at", table_name="arena_logs")
    op.drop_table("arena_logs")
