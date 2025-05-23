from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.DocenteMateria_Model import DocenteMateria
from .. import db

class DocenteMateriaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DocenteMateria
        load_instance = True
        sqla_session = db.session
        include_fk = True  # para que incluya las foreign keys
