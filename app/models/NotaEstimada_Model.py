from app import db

class NotaEstimada(db.Model):
    __tablename__ = 'nota_estimada'
    id = db.Column(db.Integer, primary_key=True)
    valor_estimado = db.Column(db.Float)
    razon_estimacion = db.Column(db.Text)
    estudiante_ci = db.Column(db.Integer, db.ForeignKey('estudiante.ci'))
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'))
    gestion_id = db.Column(db.Integer, db.ForeignKey('gestion.id'))
