from flask_restx import Namespace, Resource, fields

ns = Namespace('Porcentaje', description='Operaciones relacionadas con Porcentaje')


porcentaje_model_request = ns.model('PorcentajeRequest', {

    'porcentaje': fields.Float(required=True, description='Valor del porcentaje'),
})

porcentaje_model_response = ns.model('PorcentajeResponse', {
    'id': fields.Integer(description='ID'),
    'porcentaje': fields.Float(required=True, description='Valor del porcentaje'),
})
