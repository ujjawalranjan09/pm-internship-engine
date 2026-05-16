"""Initial schema – all tables for PM Internship Engine.

Revision ID: 001_initial
Revises: None
Create Date: 2026-05-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── ENUM types used by Allocation and AllocationCycle ──────────
    allocation_status_enum = postgresql.ENUM(
        "pending",
        "confirmed",
        "accepted",
        "declined",
        "withdrawn",
        "completed",
        name="allocation_status_enum",
        create_type=True,
    )
    cycle_status_enum = postgresql.ENUM(
        "draft",
        "running",
        "completed",
        "failed",
        "cancelled",
        name="cycle_status_enum",
        create_type=True,
    )

    # ── users ─────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="candidate", index=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── candidate_profiles ────────────────────────────────────────
    op.create_table(
        "candidate_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False, index=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("education", postgresql.JSONB(), nullable=True),
        sa.Column("skills", postgresql.JSONB(), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("district", sa.String(100), nullable=True, index=True),
        sa.Column("state", sa.String(100), nullable=True, index=True),
        sa.Column("social_category", sa.String(50), nullable=True, index=True),
        sa.Column("is_rural", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("resume_url", sa.Text(), nullable=True),
        sa.Column("profile_completion_score", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("mobility_preferences", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── opportunities ─────────────────────────────────────────────
    op.create_table(
        "opportunities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "employer_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
        ),
        sa.Column("title", sa.String(255), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("sector", sa.String(100), nullable=True, index=True),
        sa.Column("required_skills", postgresql.JSONB(), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("state", sa.String(100), nullable=True, index=True),
        sa.Column("district", sa.String(100), nullable=True, index=True),
        sa.Column("work_mode", sa.String(20), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("stipend", sa.Float(), nullable=True),
        sa.Column("duration_months", sa.Integer(), nullable=True),
        sa.Column("eligibility_criteria", postgresql.JSONB(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true"), index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── matches ───────────────────────────────────────────────────
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "candidate_id",
            sa.Integer(),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "opportunity_id",
            sa.Integer(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("score", sa.Float(), nullable=False, index=True),
        sa.Column("score_breakdown", postgresql.JSONB(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── allocation_cycles ─────────────────────────────────────────
    op.create_table(
        "allocation_cycles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("status", cycle_status_enum, nullable=False, server_default="draft", index=True),
        sa.Column("config", postgresql.JSONB(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── allocations ───────────────────────────────────────────────
    op.create_table(
        "allocations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "candidate_id",
            sa.Integer(),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "opportunity_id",
            sa.Integer(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id", ondelete="SET NULL"), nullable=True),
        sa.Column(
            "allocation_cycle_id",
            sa.Integer(),
            sa.ForeignKey("allocation_cycles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("status", allocation_status_enum, nullable=False, server_default="pending", index=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("allocated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── notifications ─────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("type", sa.String(50), nullable=False, index=True),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending", index=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── audit_logs ────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=True, index=True),
        sa.Column("action", sa.String(100), nullable=False, index=True),
        sa.Column("entity_type", sa.String(100), nullable=False, index=True),
        sa.Column("entity_id", sa.Integer(), nullable=True, index=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── waitlist_entries ──────────────────────────────────────────
    op.create_table(
        "waitlist_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "candidate_id",
            sa.Integer(),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "opportunity_id",
            sa.Integer(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "allocation_cycle_id",
            sa.Integer(),
            sa.ForeignKey("allocation_cycles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="waiting", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("waitlist_entries")
    op.drop_table("audit_logs")
    op.drop_table("notifications")
    op.drop_table("allocations")
    op.drop_table("allocation_cycles")
    op.drop_table("matches")
    op.drop_table("opportunities")
    op.drop_table("candidate_profiles")
    op.drop_table("users")

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS cycle_status_enum")
    op.execute("DROP TYPE IF EXISTS allocation_status_enum")
