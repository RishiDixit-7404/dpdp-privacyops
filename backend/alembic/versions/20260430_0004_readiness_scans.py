"""add readiness scan workflow

Revision ID: 20260430_0004
Revises: 20260426_0003
Create Date: 2026-04-30 00:00:00.000000+00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260430_0004"
down_revision: Union[str, None] = "20260426_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "readiness_scans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=False),
        sa.Column("customer_segment", sa.String(length=32), nullable=False),
        sa.Column("package_name", sa.String(length=255), nullable=False),
        sa.Column("price_inr", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("input_checklist", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "customer_segment in ('edtech', 'healthtech', 'hrtech', 'ai_saas', 'b2b_saas', 'other')",
            name="ck_readiness_scans_customer_segment",
        ),
        sa.CheckConstraint("price_inr >= 0", name="ck_readiness_scans_price_inr"),
        sa.CheckConstraint(
            "status in ('draft', 'inputs_requested', 'inputs_received', 'scanning', 'report_ready', "
            "'walkthrough_done', 'converted_to_subscription', 'closed_lost')",
            name="ck_readiness_scans_status",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_readiness_scans_project_id"), "readiness_scans", ["project_id"], unique=False)
    op.create_index(op.f("ix_readiness_scans_status"), "readiness_scans", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_readiness_scans_status"), table_name="readiness_scans")
    op.drop_index(op.f("ix_readiness_scans_project_id"), table_name="readiness_scans")
    op.drop_table("readiness_scans")
