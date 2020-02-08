"""added 2 user columns

Revision ID: 1aafbb0aaadd
Revises: be510dcc19cd
Create Date: 2020-02-07 16:17:53.532054

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1aafbb0aaadd'
down_revision = 'be510dcc19cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('athlete_id', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('number_of_activities', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'number_of_activities')
    op.drop_column('user', 'athlete_id')
    # ### end Alembic commands ###