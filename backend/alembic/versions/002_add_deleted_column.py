"""Add deleted column to task table

Revision ID: 002
Revises: 001
Create Date: 2026-01-20 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the deleted column to the task table with a default value of false
    op.add_column('task', sa.Column('deleted', sa.Boolean(), nullable=False, default=False, server_default='false'))


def downgrade() -> None:
    # Remove the deleted column from the task table
    op.drop_column('task', 'deleted')