from app import db
from .TipoEvaluacion_Model import TipoEvaluacion

class EvaluacionIntegral(db.Model):
    __tablename__ = 'evaluacion_integral'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable = False)
    maxPuntos = db.Column(db.Integer)
    # Relación: uno a muchos con TipoEvaluacion
    tipos_evaluacion = db.relationship('TipoEvaluacion', back_populates='evaluacion_integral', lazy=True)
    
