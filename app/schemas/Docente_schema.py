from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.Docente_Model import Docente
from .. import db


class DocenteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Docente
        load_instance = True
        sqla_session = db.session



