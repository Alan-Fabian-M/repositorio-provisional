from flask_restx import Namespace, Resource, fields

ns = Namespace('DocenteMateria', description='Operaciones relacionadas con docente materia')

docente_materia_model_request = ns.model('DocenteMateriaRequest', {
    'fecha': fields.Date(required=True, description='Fecha de asignación'),
    'docente_ci': fields.Integer(required=True, description='CI del docente'),
    'materia_id': fields.Integer(required=True, description='ID de la materia'),
})

docente_materia_mode_response = ns.model('DocenteMateriaResponse', {
    'id': fields.Integer(description='ID'),
    'fecha': fields.Date(required=True, description='Fecha de asignación'),
    'docente_ci': fields.Integer(required=True, description='CI del docente'),
    'materia_id': fields.Integer(required=True, description='ID de la materia'),
})
