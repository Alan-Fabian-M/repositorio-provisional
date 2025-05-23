from flask_restx import Namespace, Resource, fields

ns = Namespace('TipoEvaluacion', description='Operaciones relacionadas con Tipo Evaluacion')


tipo_evaluacion_model_request = ns.model('TipoEvaluacionRequest', {
    'nombre': fields.String(required=True, description='Nombre del tipo de evaluación'),
})

tipo_evaluacion_model_response = ns.model('TipoEvaluacionResponse', {
    'id': fields.Integer(description='ID'),
    'nombre': fields.String(required=True, description='Nombre del tipo de evaluación'),
})
