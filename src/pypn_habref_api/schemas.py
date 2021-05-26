from .models import Habref, TypoRef

from pypn_habref_api.env import MA

class TypoRefSchema(MA.SQLAlchemyAutoSchema):
    class Meta:
        model = TypoRef
        load_instance = True
        include_fk = True


class HabrefSchema(MA.SQLAlchemyAutoSchema):
    class Meta:
        model = Habref
        load_instance = True
        include_fk = True

    typo_ref = MA.Nested(TypoRefSchema, dump_only=True)

