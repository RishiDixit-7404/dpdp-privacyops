"""add project api keys

Revision ID: 20260427_0004
Revises: 20260426_0003
Create Date: 2026-04-27 00:00:00.000000+00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260427_0004"
down_revision: Union[str, None] = "20260426_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project_api_keys",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("key_prefix", sa.String(length=32), nullable=False),
        sa.Column("key_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("length(trim(key_hash)) > 0", name="ck_project_api_keys_key_hash_not_empty"),
        sa.CheckConstraint("length(trim(key_prefix)) > 0", name="ck_project_api_keys_key_prefix_not_empty"),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_project_api_keys_name_not_empty"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_api_keys_project_id"), "project_api_keys", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_api_keys_key_prefix"), "project_api_keys", ["key_prefix"], unique=False)
    op.create_index(op.f("ix_project_api_keys_revoked_at"), "project_api_keys", ["revoked_at"], unique=False)
    op.create_index(
        "ix_project_api_keys_project_prefix",
        "project_api_keys",
        ["project_id", "key_prefix"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_project_api_keys_project_prefix", table_name="project_api_keys")
    op.drop_index(op.f("ix_project_api_keys_revoked_at"), table_name="project_api_keys")
    op.drop_index(op.f("ix_project_api_keys_key_prefix"), table_name="project_api_keys")
    op.drop_index(op.f("ix_project_api_keys_project_id"), table_name="project_api_keys")
    op.drop_table("project_api_keys")
