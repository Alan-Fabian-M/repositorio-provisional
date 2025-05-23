from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.NotaEstimada_Model import NotaEstimada
from .. import db

class NotaEstimadaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = NotaEstimada
        load_instance = True
        sqla_session = db.session
        include_fk = True
