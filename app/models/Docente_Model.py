from app import db

class Docente(db.Model):
    __tablename__ = 'docente'
    ci = db.Column(db.Integer, unique = True, primary_key=True)
    nombreCompleto = db.Column(db.String(50))
    gmail = db.Column(db.String(50))
    contrasena = db.Column(db.String(255))
    esDocente = db.Column(db.Boolean)
    
    # Relación con DocenteMateria
    materias = db.relationship('DocenteMateria', back_populates='docente', lazy=True)