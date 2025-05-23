from flask_restx import Namespace, Resource, fields

ns = Namespace('Gestion', description='Operaciones relacionadas con Gestion')


gestion_model_request = ns.model('GestionRequest', {
    'anio': fields.Integer(required=True, description='Año'),
    'periodo': fields.String(required=True, description='Periodo'),
})

gestion_model_response = ns.model('GestionResponse', {
    'id': fields.Integer(description='ID'),
    'anio': fields.Integer(required=True, description='Año'),
    'periodo': fields.String(required=True, description='Periodo'),
})
