from flask_restx import Namespace, Resource, fields

ns = Namespace('EvaluacionIntegral', description='Operaciones relacionadas con Evaluacion Integral')


EvaluacionIntegral_model_request = ns.model('EvaluacionIntegralRequest', {

    'nombre': fields.String(required=True, description='Nombre de la evaluacion integral'),
    'maxPuntos': fields.Integer(required=True, description='Max_puntos que se le asignan'),
})

EvaluacionIntegral_model_response = ns.model('EvaluacionIntegralResponse', {
    'id': fields.Integer(description='ID'),
    'nombre': fields.String(required=True, description='Nombre de la evaluacion integral'),
    'maxPuntos': fields.Integer(required=True, description='Max_puntos que se le asignan'),
})
