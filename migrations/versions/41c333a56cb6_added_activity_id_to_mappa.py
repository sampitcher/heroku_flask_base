"""added activity_id to mappa

Revision ID: 41c333a56cb6
Revises: 19609f87f94f
Create Date: 2020-04-14 20:02:51.406286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41c333a56cb6'
down_revision = '19609f87f94f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mappa', sa.Column('activity_id', sa.String(length=140), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mappa', 'activity_id')
    # ### end Alembic commands ###