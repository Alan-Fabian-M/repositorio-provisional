from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.NotaFinal_Model import NotaFinal
from .. import db

class NotaFinalSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = NotaFinal
        load_instance = True
        sqla_session = db.session
        include_fk = True
