from app import db

class Inscripcion(db.Model):
    __tablename__ = 'inscripcion'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100))
    fecha = db.Column(db.Date)
    estudiante_ci = db.Column(db.Integer, db.ForeignKey('estudiante.ci'))
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'))
