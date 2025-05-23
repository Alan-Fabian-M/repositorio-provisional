from flask_restx import Namespace, Resource, fields

ns = Namespace('TipoEvaluacion', description='Operaciones relacionadas con Tipo Evaluacion')


tipo_evaluacion_model = ns.model('TipoEvaluacion', {
    'id': fields.Integer(description='ID'),
    'nombre': fields.String(required=True, description='Nombre del tipo de evaluación'),
})
