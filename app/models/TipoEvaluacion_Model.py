from app import db


class TipoEvaluacion(db.Model):
    __tablename__ = 'tipo_evaluacion'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
