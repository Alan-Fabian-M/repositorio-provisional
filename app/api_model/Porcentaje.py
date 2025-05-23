from flask_restx import Namespace, Resource, fields

ns = Namespace('Porcentaje', description='Operaciones relacionadas con Porcentaje')


porcentaje_model = ns.model('Porcentaje', {
    'id': fields.Integer(description='ID'),
    'porcentaje': fields.Float(required=True, description='Valor del porcentaje'),
})
