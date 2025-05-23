"""fix

Revision ID: 96b0554b8bd7
Revises: 538030160913
Create Date: 2024-06-22 12:16:00.528105

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '96b0554b8bd7'
down_revision = '538030160913'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('text', sa.String(), nullable=True))
        batch_op.drop_column('price')
        batch_op.drop_column('description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', mysql.TEXT(), nullable=True))
        batch_op.add_column(sa.Column('price', mysql.FLOAT(), nullable=False))
        batch_op.drop_column('text')

    # ### end Alembic commands ###
