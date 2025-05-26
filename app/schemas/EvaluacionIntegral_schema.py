from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.EvaluacionIntegral_Model import EvaluacionIntegral
from .. import db

class EvaluacionIntegralSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EvaluacionIntegral
        load_instance = True
        sqla_session = db.session
        include_fk = True
