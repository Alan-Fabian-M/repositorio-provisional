from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.Evaluacion_Model import Evaluacion
from .. import db

class EvaluacionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Evaluacion
        load_instance = True
        sqla_session = db.session
        include_fk = True
