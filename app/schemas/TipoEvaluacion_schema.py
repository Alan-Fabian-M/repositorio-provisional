from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.TipoEvaluacion_Model import TipoEvaluacion
from .. import db

class TipoEvaluacionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TipoEvaluacion
        load_instance = True
        sqla_session = db.session
