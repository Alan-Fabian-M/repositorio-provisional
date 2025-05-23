from app import db

class Porcentaje(db.Model):
    __tablename__ = 'porcentaje'
    id = db.Column(db.Integer, primary_key=True)
    porcentaje = db.Column(db.Float)
