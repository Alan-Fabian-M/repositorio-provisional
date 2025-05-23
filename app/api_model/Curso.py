from flask_restx import Namespace, Resource, fields

ns = Namespace('Curso', description='Operaciones relacionadas con curso')


curso_model_request = ns.model('Curso', {
    'nombre': fields.String(required=True, description='Nombre del curso'),
    'Paralelo': fields.String(description='A que paralelo pertenece el curso'),
    'Turno': fields.String(description='Turno del curso (mañana, tarde o noche)'),
    'Nivel': fields.String(description='Nivel del curso(primaria, secundaria, nidito)'),
    'descripcion': fields.String(description='Descripción del curso'),
})

curso_model_response = ns.inherit('Curso Response', curso_model_request, {
    'id': fields.Integer(description='ID del curso'),
})
