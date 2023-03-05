"""Add user table

Revision ID: 864228f93aac
Revises: 
Create Date: 2023-03-03 14:33:27.698405

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "864228f93aac"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("login", sa.String(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("picture", sqlalchemy_utils.types.url.URLType(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("login"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###