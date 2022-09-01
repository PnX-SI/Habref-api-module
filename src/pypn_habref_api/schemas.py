from pypn_habref_api.models import Habref, TypoRef
from pypn_habref_api.env import ma


class TypoRefSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TypoRef
        load_instance = True
        include_fk = True


class HabrefSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Habref
        load_instance = True
        include_fk = True

    typo_ref = ma.Nested(TypoRefSchema, dump_only=True)
