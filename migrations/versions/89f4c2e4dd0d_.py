"""empty message

Revision ID: 89f4c2e4dd0d
Revises: 21a8152d4580
Create Date: 2022-02-13 20:23:30.260407

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "89f4c2e4dd0d"
down_revision = "21a8152d4580"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("houses_name_datetime_key", "houses", type_="unique")
    op.create_unique_constraint(None, "houses", ["name"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "houses", type_="unique")
    op.create_unique_constraint("houses_name_datetime_key", "houses", ["name", "datetime"])
    # ### end Alembic commands ###
