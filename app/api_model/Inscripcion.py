from flask_restx import Namespace, Resource, fields

ns = Namespace('Inscripcion', description='Operaciones relacionadas con Incripcion')


inscripcion_model_request = ns.model('InscripcionRequest', {
    'descripcion': fields.String(description='Descripción'),
    'fecha': fields.Date(required=True, description='Fecha de inscripción'),
    'estudiante_ci': fields.Integer(required=True, description='CI del estudiante'),
    'curso_id': fields.Integer(required=True, description='ID del curso'),
})

inscripcion_model_response = ns.model('InscripcionResponse', {
    'id': fields.Integer(description='ID'),
    'descripcion': fields.String(description='Descripción'),
    'fecha': fields.Date(required=True, description='Fecha de inscripción'),
    'estudiante_ci': fields.Integer(required=True, description='CI del estudiante'),
    'curso_id': fields.Integer(required=True, description='ID del curso'),
})
