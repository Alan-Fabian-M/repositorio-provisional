from flask_restx import Namespace, Resource, fields

ns = Namespace('NotaFinal', description='Operaciones relacionadas con Nota Final')


nota_final_model_request = ns.model('NotaFinalRequest', {
    'valor': fields.Float(required=True, description='Nota final'),
    'estudiante_ci': fields.Integer(required=True, description='CI del estudiante'),
    'materia_id': fields.Integer(required=True, description='ID de la materia'),
})

nota_final_model_response = ns.model('NotaFinalResponse', {
    'id': fields.Integer(description='ID'),
    'valor': fields.Float(required=True, description='Nota final'),
    'estudiante_ci': fields.Integer(required=True, description='CI del estudiante'),
    'materia_id': fields.Integer(required=True, description='ID de la materia'),
})
