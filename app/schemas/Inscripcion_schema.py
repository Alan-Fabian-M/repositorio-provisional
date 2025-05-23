from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.Inscripcion_Model import Inscripcion
from .. import db

class InscripcionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inscripcion
        load_instance = True
        sqla_session = db.session
        include_fk = True
