from flask_restx import Namespace, Resource, fields

ns = Namespace('NotaEstimada', description='Operaciones relacionadas con Nota Estimada')

nota_estimada_model = ns.model('NotaEstimada', {
    'id': fields.Integer(description='ID'),
    'valor_estimado': fields.Float(required=True, description='Valor estimado'),
    'razon_estimacion': fields.String(description='Razón de la estimación'),
    'estudiante_ci': fields.Integer(required=True, description='CI del estudiante'),
    'materia_id': fields.Integer(required=True, description='ID de la materia'),
})
