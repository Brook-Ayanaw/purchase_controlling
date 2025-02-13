"""added a payment file name

Revision ID: 62f4acfda16f
Revises: 32d11a21c4d1
Create Date: 2024-08-01 11:48:07.329551

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62f4acfda16f'
down_revision = '32d11a21c4d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_file_name', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('payment_file_name')

    # ### end Alembic commands ###
