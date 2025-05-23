from flask_restx import Namespace, Resource, fields

ns = Namespace('NotaFinal', description='Operaciones relacionadas con Nota Final')


nota_final_model = ns.model('NotaFinal', {
    'id': fields.Integer(description='ID'),
    'valor': fields.Float(required=True, description='Nota final'),
    'estudiante_ci': fields.Integer(required=True, description='CI del estudiante'),
    'materia_id': fields.Integer(required=True, description='ID de la materia'),
})
