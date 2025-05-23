from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.Porcentaje_Model import Porcentaje
from .. import db

class PorcentajeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Porcentaje
        load_instance = True
        sqla_session = db.session
        include_fk = True
