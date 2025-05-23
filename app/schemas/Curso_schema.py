from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from ..models.Curso_Model import Curso
from ..schemas.MateriaCurso_schema import MateriaCursoSchema
from .. import db

class CursoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Curso
        load_instance = True
        sqla_session = db.session

    materias = fields.Nested(MateriaCursoSchema, many=True)
