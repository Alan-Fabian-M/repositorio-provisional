from flask_restx import Namespace, Resource, fields

ns = Namespace('TipoEvaluacion', description='Operaciones relacionadas con Tipo Evaluacion')


tipo_evaluacion_model_request = ns.model('TipoEvaluacionRequest', {
    'nombre': fields.String(required=True, description='Nombre del tipo de evaluación'),
    'evaluacion_integral_id': fields.Integer(description='Id de la evaluacion integral')
})

tipo_evaluacion_model_response = ns.model('TipoEvaluacionResponse', {
    'id': fields.Integer(description='ID'),
    'nombre': fields.String(required=True, description='Nombre del tipo de evaluación'),
    'evaluacion_integral_id': fields.Integer(description='Id de la evaluacion integral')
})
