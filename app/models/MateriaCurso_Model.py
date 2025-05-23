from app import db

class MateriaCurso(db.Model):
    __tablename__ = 'materia_curso'
    id = db.Column(db.Integer, primary_key=True)
    anio = db.Column(db.Integer)

    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'))
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'))

    materia = db.relationship('Materia', back_populates='cursos')
    curso = db.relationship('Curso', back_populates='materias')
