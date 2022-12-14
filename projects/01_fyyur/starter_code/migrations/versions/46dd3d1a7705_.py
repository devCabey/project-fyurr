"""empty message

Revision ID: 46dd3d1a7705
Revises: 8409b6a55357
Create Date: 2022-08-12 04:28:11.718224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46dd3d1a7705'
down_revision = '8409b6a55357'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('artist_id', sa.Integer(), nullable=True))
    op.add_column('Show', sa.Column('venue_id', sa.Integer(), nullable=True))
    op.drop_constraint('Show_artist_fkey', 'Show', type_='foreignkey')
    op.drop_constraint('Show_venue_fkey', 'Show', type_='foreignkey')
    op.create_foreign_key(None, 'Show', 'Artist', ['artist_id'], ['id'])
    op.create_foreign_key(None, 'Show', 'Venue', ['venue_id'], ['id'])
    op.drop_column('Show', 'artist')
    op.drop_column('Show', 'venue')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('venue', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('artist', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.create_foreign_key('Show_venue_fkey', 'Show', 'Venue', ['venue'], ['id'])
    op.create_foreign_key('Show_artist_fkey', 'Show', 'Artist', ['artist'], ['id'])
    op.drop_column('Show', 'venue_id')
    op.drop_column('Show', 'artist_id')
    # ### end Alembic commands ###
