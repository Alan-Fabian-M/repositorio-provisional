from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.MateriaCurso_Model import MateriaCurso
from .. import db

class MateriaCursoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MateriaCurso
        load_instance = True
        sqla_session = db.session
        include_fk = True
