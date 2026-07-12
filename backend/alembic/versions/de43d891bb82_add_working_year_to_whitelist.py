"""add working year to whitelist

Revision ID: de43d891bb82
Revises: 45e6003a255d
Create Date: 2026-06-25 00:19:32.325485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "de43d891bb82"
down_revision: Union[str, Sequence[str], None] = "45e6003a255d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("white_list", sa.Column("working_year", sa.Integer(), nullable=True))
    op.drop_column("white_list", "updated_at")
    op.drop_column("white_list", "created_at")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("white_list", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("white_list", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.drop_column("white_list", "working_year")
