from importlib import import_module

from flask import current_app

from .models import Habref, TypoRef

MA = current_app.config.get("MA", import_module(".env", "pypn_habref_api").MA)


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

