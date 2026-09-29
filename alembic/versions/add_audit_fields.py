
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "add_audit_fields"
down_revision = "7f8aa5f14746"
branch_labels = None
depends_on = None


def upgrade():

    # -------------------------------
    # Doctors
    # -------------------------------

    op.add_column(
        "doctors",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "doctors",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "doctors",
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "doctors",
        sa.Column(
            "updated_by",
            sa.Integer(),
            nullable=True
        )
    )


    # -------------------------------
    # Patients
    # -------------------------------

    op.add_column(
        "patients",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "patients",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "patients",
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "patients",
        sa.Column(
            "updated_by",
            sa.Integer(),
            nullable=True
        )
    )


    # -------------------------------
    # Appointments
    # -------------------------------

    op.add_column(
        "appointments",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "appointments",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "appointments",
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "appointments",
        sa.Column(
            "updated_by",
            sa.Integer(),
            nullable=True
        )
    )


def downgrade():

    # -------------------------------
    # Appointments
    # -------------------------------

    op.drop_column(
        "appointments",
        "updated_by"
    )

    op.drop_column(
        "appointments",
        "created_by"
    )

    op.drop_column(
        "appointments",
        "updated_at"
    )

    op.drop_column(
        "appointments",
        "created_at"
    )


    # -------------------------------
    # Patients
    # -------------------------------

    op.drop_column(
        "patients",
        "updated_by"
    )

    op.drop_column(
        "patients",
        "created_by"
    )

    op.drop_column(
        "patients",
        "updated_at"
    )

    op.drop_column(
        "patients",
        "created_at"
    )


    # -------------------------------
    # Doctors
    # -------------------------------

    op.drop_column(
        "doctors",
        "updated_by"
    )

    op.drop_column(
        "doctors",
        "created_by"
    )

    op.drop_column(
        "doctors",
        "updated_at"
    )

    op.drop_column(
        "doctors",
        "created_at"
    )
