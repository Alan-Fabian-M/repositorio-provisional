from app import db

class Evaluacion(db.Model):
    __tablename__ = 'evaluacion'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.Date)
    nota = db.Column(db.Float)

    tipo_evaluacion_id = db.Column(db.Integer, db.ForeignKey('tipo_evaluacion.id'))
    estudiante_ci = db.Column(db.Integer, db.ForeignKey('estudiante.ci'))
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'))
    gestion_id = db.Column(db.Integer, db.ForeignKey('gestion.id'))