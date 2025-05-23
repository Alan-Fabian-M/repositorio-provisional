from app import db


class DocenteMateria(db.Model):
    __tablename__ = 'docente_materia'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date)

    docente_ci = db.Column(db.Integer, db.ForeignKey('docente.ci'))
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'))

    # Relaciones hacia ambos lados
    docente = db.relationship('Docente', back_populates='materias')
    materia = db.relationship('Materia', back_populates='docentes')
