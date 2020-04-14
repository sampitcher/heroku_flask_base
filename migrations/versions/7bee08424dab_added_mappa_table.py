"""added mappa table

Revision ID: 7bee08424dab
Revises: 5c3aef470fcd
Create Date: 2020-04-14 16:25:46.461888

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bee08424dab'
down_revision = '5c3aef470fcd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mappa',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mappa_id', sa.String(length=140), nullable=True),
    sa.Column('name', sa.String(length=140), nullable=True),
    sa.Column('epoch', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('elevation', sa.String(length=64), nullable=True),
    sa.Column('distance', sa.String(length=64), nullable=True),
    sa.Column('duration', sa.String(length=64), nullable=True),
    sa.Column('max_speed', sa.String(length=64), nullable=True),
    sa.Column('avg_speed', sa.String(length=64), nullable=True),
    sa.Column('max_power', sa.String(length=64), nullable=True),
    sa.Column('avg_power', sa.String(length=64), nullable=True),
    sa.Column('max_heartrate', sa.String(length=64), nullable=True),
    sa.Column('avg_heartrate', sa.String(length=64), nullable=True),
    sa.Column('name_id', sa.String(length=128), nullable=True),
    sa.Column('icon_url', sa.String(length=128), nullable=True),
    sa.Column('altitude_url', sa.String(length=128), nullable=True),
    sa.Column('mappa_url', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mappa')
    # ### end Alembic commands ###
