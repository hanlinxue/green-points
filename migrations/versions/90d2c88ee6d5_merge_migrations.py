"""merge migrations

Revision ID: 90d2c88ee6d5
Revises: add_points_exchange_rate, add_withdrawal_record
Create Date: 2025-12-14 00:59:32.602034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90d2c88ee6d5'
down_revision = ('add_points_exchange_rate', 'add_withdrawal_record')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
