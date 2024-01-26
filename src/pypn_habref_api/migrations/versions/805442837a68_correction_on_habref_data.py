"""correction on habref data

Column lb_hab_en and lb_auteur were switched in insertion...
Revision ID: 805442837a68
Revises: 46e91e738845
Create Date: 2021-11-08 17:05:39.425755

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "805442837a68"
down_revision = "46e91e738845"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE ref_habitats.habref ADD column lb_hab_en_save character varying(500);
        UPDATE ref_habitats.habref 
        SET lb_hab_en_save = lb_auteur;
        UPDATE ref_habitats.habref 
        SET lb_auteur = lb_hab_en;
        UPDATE ref_habitats.habref 
        SET lb_hab_en = lb_hab_en_save;
        ALTER TABLE ref_habitats.habref DROP column lb_hab_en_save
    """
    )
    op.execute(
        """
        DELETE FROM ref_habitats.autocomplete_habitat;
        INSERT INTO ref_habitats.autocomplete_habitat
        SELECT 
        cd_hab,
        h.cd_typo,
        lb_code,
        lb_nom_typo,
        concat(lb_code, ' - ', lb_hab_fr, ' ', lb_hab_fr_complet)
        FROM ref_habitats.habref h
        JOIN ref_habitats.typoref t ON t.cd_typo = h.cd_typo;
    """
    )


def downgrade():
    pass
