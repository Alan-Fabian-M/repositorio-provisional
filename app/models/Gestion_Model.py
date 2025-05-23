from app import db


class Gestion(db.Model):
    __tablename__ = 'gestion'
    id = db.Column(db.Integer, primary_key=True)
    anio = db.Column(db.Integer)
    periodo = db.Column(db.String(50))
