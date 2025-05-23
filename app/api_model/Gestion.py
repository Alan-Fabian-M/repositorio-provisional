from flask_restx import Namespace, Resource, fields

ns = Namespace('Gestion', description='Operaciones relacionadas con Gestion')


gestion_model = ns.model('Gestion', {
    'id': fields.Integer(description='ID'),
    'anio': fields.Integer(required=True, description='Año'),
    'periodo': fields.String(required=True, description='Periodo'),
})
