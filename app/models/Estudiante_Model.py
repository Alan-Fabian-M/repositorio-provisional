from app import db

class Estudiante(db.Model):
    __tablename__ = 'estudiante'
    ci = db.Column(db.Integer, unique = True, primary_key=True)
    nombreCompleto = db.Column(db.String(50))
    fechaNacimiento = db.Column(db.Date)
    apoderado = db.Column(db.String(255))
    telefono = db.Column(db.String(50))
    imagen_url = db.Column(db.String(500))
    imagen_public_id = db.Column(db.String(500))
