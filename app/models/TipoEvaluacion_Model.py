from app import db


class TipoEvaluacion(db.Model):
    __tablename__ = 'tipo_evaluacion'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    # FK hacia EvaluacionIntegral
    evaluacion_integral_id = db.Column(db.Integer, db.ForeignKey('evaluacion_integral.id'))

    # Relación inversa (opcional, si quieres acceder desde EvaluacionIntegral)
    evaluacion_integral = db.relationship('EvaluacionIntegral', back_populates='tipos_evaluacion')
