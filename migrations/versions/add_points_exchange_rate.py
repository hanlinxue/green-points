"""添加积分兑换现实货币汇率表

Revision ID: add_points_exchange_rate
Revises: 83ec01ae1a9a
Create Date: 2025-12-13 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_points_exchange_rate'
down_revision = '83ec01ae1a9a'
branch_labels = None
depends_on = None


def upgrade():
    # 创建积分兑换现实货币汇率表
    op.create_table(
        'tb_points_exchange_rate',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, comment='主键ID'),
        sa.Column('currency_code', sa.String(10), nullable=False, comment='货币代码（如：CNY、USD、EUR）'),
        sa.Column('currency_name', sa.String(50), nullable=False, comment='货币名称（如：人民币、美元、欧元）'),
        sa.Column('exchange_rate', sa.Numeric(10, 4), nullable=False, comment='兑换汇率（1积分=X货币）'),
        sa.Column('symbol', sa.String(10), nullable=False, comment='货币符号（如：¥、$、€）'),
        sa.Column('is_active', sa.Boolean(), default=True, comment='是否启用'),
        sa.Column('rdatetime', sa.DateTime(), default=sa.text('now()'), comment='创建时间'),
        sa.Column('udatetime', sa.DateTime(), default=sa.text('now()'), onupdate=sa.text('now()'), comment='更新时间')
    )

    # 添加唯一索引
    op.create_index('idx_currency_code', 'tb_points_exchange_rate', ['currency_code'], unique=True)


def downgrade():
    # 删除表
    op.drop_table('tb_points_exchange_rate')