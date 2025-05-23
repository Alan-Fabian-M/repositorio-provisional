from flask_restx import Namespace, Resource, fields

ns = Namespace('Evaluacion', description='Operaciones relacionadas con evaluacion')


evaluacion_model_request = ns.model('EvaluacionRequest', {
    'descripcion': fields.String(description='Descripción de la evaluación'),
    'fecha': fields.Date(required=True, description='Fecha'),
    'nota': fields.Float(required=True, description='Nota'),
    'tipo_evaluacion_id': fields.Integer(required=True, description='ID del tipo de evaluación'),
    'porcentaje_id': fields.Integer(required=True, description='ID del porcentaje'),
    'estudiante_ci': fields.Integer(required=True, description='CI del estudiante'),
    'materia_id': fields.Integer(required=True, description='ID de la materia'),
})

evaluacion_model_response = ns.model('EvaluacionResponse', {
    'id': fields.Integer(description='ID'),
    'descripcion': fields.String(description='Descripción de la evaluación'),
    'fecha': fields.Date(required=True, description='Fecha'),
    'nota': fields.Float(required=True, description='Nota'),
    'tipo_evaluacion_id': fields.Integer(required=True, description='ID del tipo de evaluación'),
    'porcentaje_id': fields.Integer(required=True, description='ID del porcentaje'),
    'estudiante_ci': fields.Integer(required=True, description='CI del estudiante'),
    'materia_id': fields.Integer(required=True, description='ID de la materia'),
})
