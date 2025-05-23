from app import db

class Materia(db.Model):
    __tablename__ = 'materia'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    codigo = db.Column(db.String(50), unique=True)

    # Relación con MateriaCurso
    cursos = db.relationship('MateriaCurso', back_populates='materia', lazy=True, cascade='all, delete-orphan')

    # Relación con DocenteMateria
    docentes = db.relationship('DocenteMateria', back_populates='materia', lazy=True, cascade='all, delete-orphan')
