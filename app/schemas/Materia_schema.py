from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from ..models.Materia_Model import Materia
from ..schemas.DocenteMateria_schema import DocenteMateriaSchema
from ..schemas.MateriaCurso_schema import MateriaCursoSchema
from .. import db

class MateriaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Materia
        load_instance = True
        sqla_session = db.session

    docentes = fields.Nested(DocenteMateriaSchema, many=True)
    cursos = fields.Nested(MateriaCursoSchema, many=True)
