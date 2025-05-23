from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from ..models.Docente_Model import Docente
from ..schemas.DocenteMateria_schema import DocenteMateriaSchema
from .. import db

class DocenteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Docente
        load_instance = True
        sqla_session = db.session

    materias = fields.Nested(DocenteMateriaSchema, many=True)
