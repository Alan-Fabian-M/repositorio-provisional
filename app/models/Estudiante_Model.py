from app import db

class Estudiante(db.Model):
    __tablename__ = 'estudiante'
    ci = db.Column(db.Integer, unique = True, primary_key=True)
    nombreCompleto = db.Column(db.String(50))
    fechaNacimiento = db.Column(db.Date)
    contrasena = db.Column(db.String(255))
    apoderado = db.Column(db.String(255))
    telefono = db.Column(db.String(50))
