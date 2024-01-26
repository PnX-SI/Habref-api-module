"""create ref_habitats schema

Revision ID: 62e63cd6135d
Create Date: 2021-08-24 15:39:57.784074

"""

import importlib.resources

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "62e63cd6135d"
down_revision = None
branch_labels = ("habitats",)
depends_on = None


def upgrade():
    op.execute(importlib.resources.read_text("pypn_habref_api.data", "habref.sql"))


def downgrade():
    op.execute("DROP SCHEMA ref_habitats CASCADE")
