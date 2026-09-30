"""add billing module

Revision ID: 424bd3625681
Revises: add_audit_fields
Create Date: 2026-09-30 10:54:56.852592

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "424bd3625681"
down_revision: Union[str, Sequence[str], None] = "add_audit_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create billings table."""

    op.create_table(
        "billings",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "patient_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "doctor_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "appointment_id",
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            "consultation_fee",
            sa.Numeric(10, 2),
            nullable=False
        ),

        sa.Column(
            "additional_charges",
            sa.Numeric(10, 2),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "total_amount",
            sa.Numeric(10, 2),
            nullable=False
        ),

        sa.Column(
            "payment_status",
            sa.String(),
            nullable=False,
            server_default="pending"
        ),

        sa.Column(
            "payment_mode",
            sa.String(),
            nullable=True
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False
        ),

        sa.CheckConstraint(
            "consultation_fee >= 0",
            name="ck_billings_consultation_fee_non_negative"
        ),

        sa.CheckConstraint(
            "additional_charges >= 0",
            name="ck_billings_additional_charges_non_negative"
        ),

        sa.CheckConstraint(
            "total_amount >= 0",
            name="ck_billings_total_amount_non_negative"
        ),

        sa.CheckConstraint(
            "payment_status IN ('pending', 'paid', 'cancelled')",
            name="ck_billings_payment_status"
        ),

        sa.CheckConstraint(
            "payment_mode IS NULL OR payment_mode IN ('cash', 'card', 'upi')",
            name="ck_billings_payment_mode"
        ),

        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"]
        ),

        sa.ForeignKeyConstraint(
            ["doctor_id"],
            ["doctors.id"]
        ),

        sa.ForeignKeyConstraint(
            ["appointment_id"],
            ["appointments.id"]
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "appointment_id",
            name="uq_billings_appointment_id"
        )
    )

    op.create_index(
        "ix_billings_id",
        "billings",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_billings_patient_id",
        "billings",
        ["patient_id"],
        unique=False
    )

    op.create_index(
        "ix_billings_doctor_id",
        "billings",
        ["doctor_id"],
        unique=False
    )

    op.create_index(
        "ix_billings_appointment_id",
        "billings",
        ["appointment_id"],
        unique=False
    )


def downgrade() -> None:
    """Remove billings table."""

    op.drop_index(
        "ix_billings_appointment_id",
        table_name="billings"
    )

    op.drop_index(
        "ix_billings_doctor_id",
        table_name="billings"
    )

    op.drop_index(
        "ix_billings_patient_id",
        table_name="billings"
    )

    op.drop_index(
        "ix_billings_id",
        table_name="billings"
    )

    op.drop_table("billings")