"""Update User model with authentication fields and simplify Course table column names.

Revision ID: 4d1384156f0c
Revises: 28308e1e2991
Create Date: 2025-04-15 21:23:12.935599

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4d1384156f0c"
down_revision = "28308e1e2991"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "course",
        sa.Column(
            "title", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
    )
    op.add_column("course", sa.Column("description", sa.TEXT(), nullable=True))
    op.alter_column(
        "course",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
    )
    op.drop_column("course", "course_title")
    op.drop_column("course", "course_description")
    op.add_column("user", sa.Column("is_superuser", sa.Boolean(), nullable=False))
    op.add_column("user", sa.Column("is_active", sa.Boolean(), nullable=False))
    op.add_column(
        "user",
        sa.Column(
            "hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "hashed_password")
    op.drop_column("user", "is_active")
    op.drop_column("user", "is_superuser")
    op.add_column(
        "course",
        sa.Column("course_description", sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "course",
        sa.Column(
            "course_title", sa.VARCHAR(length=255), autoincrement=False, nullable=False
        ),
    )
    op.alter_column(
        "course",
        "created_at",
        existing_type=sa.DateTime(),
        type_=postgresql.TIMESTAMP(timezone=True),
        existing_nullable=False,
    )
    op.drop_column("course", "description")
    op.drop_column("course", "title")
    # ### end Alembic commands ###
