from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.Gestion_Model import Gestion
from .. import db

class GestionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Gestion
        load_instance = True
        sqla_session = db.session
