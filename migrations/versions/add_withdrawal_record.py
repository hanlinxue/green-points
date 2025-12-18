"""add withdrawal record table

Revision ID: add_withdrawal_record
Revises: add_points_exchange_rate
Create Date: 2023-12-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_withdrawal_record'
down_revision = 'e6f7e6e7f9ec'  # 使用当前的头部版本作为父版本
branch_labels = None
depends_on = None


def upgrade():
    # 创建提现记录表
    op.create_table(
        'tb_withdrawal_record',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, comment='提现记录ID'),
        sa.Column('withdrawal_no', sa.String(32), unique=True, nullable=False, comment='提现单号'),
        sa.Column('merchant_username', sa.String(30), sa.ForeignKey('tb_merchant.username'), nullable=False, comment='商户ID'),
        sa.Column('points_amount', sa.Integer, nullable=False, comment='提现积分数量'),
        sa.Column('cash_amount', sa.Numeric(10, 2), nullable=False, comment='提现金额（人民币）'),
        sa.Column('exchange_rate', sa.Numeric(10, 2), nullable=False, comment='提现时使用的汇率'),
        sa.Column('status', sa.SmallInteger, nullable=False, default=0, comment='提现状态：0-待审核 1-审核通过 2-审核拒绝 3-提现完成 4-提现失败'),
        sa.Column('bank_account', sa.String(50), nullable=True, comment='银行账号'),
        sa.Column('bank_name', sa.String(100), nullable=True, comment='银行名称'),
        sa.Column('account_holder', sa.String(50), nullable=True, comment='账户持有人'),
        sa.Column('remark', sa.String(200), nullable=True, comment='备注'),
        sa.Column('admin_remark', sa.String(200), nullable=True, comment='管理员备注'),
        sa.Column('create_time', sa.DateTime, nullable=False, comment='申请时间'),
        sa.Column('update_time', sa.DateTime, nullable=False, comment='更新时间'),
        sa.Column('approve_time', sa.DateTime, nullable=True, comment='审核时间'),
        sa.Column('complete_time', sa.DateTime, nullable=True, comment='完成时间'),
        comment='提现记录表'
    )

    # 创建索引
    op.create_index('idx_withdrawal_merchant', 'tb_withdrawal_record', ['merchant_username'])
    op.create_index('idx_withdrawal_status', 'tb_withdrawal_record', ['status'])
    op.create_index('idx_withdrawal_create_time', 'tb_withdrawal_record', ['create_time'])


def downgrade():
    # 删除索引
    op.drop_index('idx_withdrawal_create_time', 'tb_withdrawal_record')
    op.drop_index('idx_withdrawal_status', 'tb_withdrawal_record')
    op.drop_index('idx_withdrawal_merchant', 'tb_withdrawal_record')

    # 删除提现记录表
    op.drop_table('tb_withdrawal_record')