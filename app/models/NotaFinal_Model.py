from app import db

class NotaFinal(db.Model):
    __tablename__ = 'nota_final'
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float)
    estudiante_ci = db.Column(db.Integer, db.ForeignKey('estudiante.ci'))
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'))
