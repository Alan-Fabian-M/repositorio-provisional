from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from ..models.Estudiante_Model import Estudiante
from .. import db


class EstudianteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Estudiante
        load_instance = True
        sqla_session = db.session



