"""Add icon_url, color_code in categories_groups model

Revision ID: 7fdc8513226f
Revises: db2bb7068c2e
Create Date: 2023-05-05 16:16:38.524832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fdc8513226f'
down_revision = 'db2bb7068c2e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('categories_groups', sa.Column('icon_url', sa.String(), nullable=False))
    op.add_column('categories_groups', sa.Column('color_code', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('categories_groups', 'color_code')
    op.drop_column('categories_groups', 'icon_url')
    # ### end Alembic commands ###
