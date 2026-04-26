"""create scanner upload backend tables

Revision ID: 20260426_0001
Revises:
Create Date: 2026-04-26 00:00:00.000000+00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260426_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_organization_id"), "projects", ["organization_id"], unique=False)

    op.create_table(
        "scans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("scanner_scan_id", sa.String(length=128), nullable=False),
        sa.Column("scanner_version", sa.String(length=64), nullable=False),
        sa.Column("scan_type", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=512), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_pii_uploaded", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("raw_pii_uploaded = false", name="ck_scans_raw_pii_uploaded_false"),
        sa.CheckConstraint("scan_type in ('csv', 'postgres', 'json')", name="ck_scans_scan_type"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scans_project_id"), "scans", ["project_id"], unique=False)
    op.create_index(op.f("ix_scans_scanner_scan_id"), "scans", ["scanner_scan_id"], unique=True)

    op.create_table(
        "findings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scan_id", sa.Uuid(), nullable=False),
        sa.Column("scanner_finding_id", sa.String(length=128), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_name", sa.String(length=512), nullable=False),
        sa.Column("table_or_file", sa.String(length=512), nullable=False),
        sa.Column("field_name", sa.String(length=512), nullable=False),
        sa.Column("pii_type", sa.String(length=128), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("detection_method", sa.String(length=32), nullable=False),
        sa.Column("masked_examples", sa.JSON(), nullable=False),
        sa.Column("sample_count", sa.Integer(), nullable=False),
        sa.Column("match_count", sa.Integer(), nullable=False),
        sa.Column("suggested_action", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("confidence_score >= 0 and confidence_score <= 1", name="ck_findings_confidence_score"),
        sa.CheckConstraint("detection_method in ('column_name', 'regex_value', 'combined')", name="ck_findings_detection_method"),
        sa.CheckConstraint("match_count >= 0", name="ck_findings_match_count"),
        sa.CheckConstraint("risk_level in ('low', 'medium', 'high', 'critical')", name="ck_findings_risk_level"),
        sa.CheckConstraint("sample_count >= 0", name="ck_findings_sample_count"),
        sa.CheckConstraint("source_type in ('csv', 'postgres', 'json')", name="ck_findings_source_type"),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scan_id", "scanner_finding_id", name="uq_findings_scan_scanner_finding_id"),
    )
    op.create_index(op.f("ix_findings_pii_type"), "findings", ["pii_type"], unique=False)
    op.create_index(op.f("ix_findings_risk_level"), "findings", ["risk_level"], unique=False)
    op.create_index(op.f("ix_findings_scan_id"), "findings", ["scan_id"], unique=False)
    op.create_index(op.f("ix_findings_scanner_finding_id"), "findings", ["scanner_finding_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_findings_scanner_finding_id"), table_name="findings")
    op.drop_index(op.f("ix_findings_scan_id"), table_name="findings")
    op.drop_index(op.f("ix_findings_risk_level"), table_name="findings")
    op.drop_index(op.f("ix_findings_pii_type"), table_name="findings")
    op.drop_table("findings")
    op.drop_index(op.f("ix_scans_scanner_scan_id"), table_name="scans")
    op.drop_index(op.f("ix_scans_project_id"), table_name="scans")
    op.drop_table("scans")
    op.drop_index(op.f("ix_projects_organization_id"), table_name="projects")
    op.drop_table("projects")
    op.drop_table("organizations")

