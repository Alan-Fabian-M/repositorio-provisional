from flask_restx import Namespace, Resource, fields

ns = Namespace('MateriasCurso', description='Operaciones relacionadas con materia curso')


materia_curso_model_request = ns.model('MateriaCursorequest', {
    'anio': fields.Integer(required=True, description='Año'),
    'materia_id': fields.Integer(required=True, description='ID de la materia'),
    'curso_id': fields.Integer(required=True, description='ID del curso'),
})

materia_curso_model_response = ns.model('MateriaCursoResponse', {
    'id': fields.Integer(description='ID'),
    'anio': fields.Integer(required=True, description='Año'),
    'materia_id': fields.Integer(required=True, description='ID de la materia'),
    'curso_id': fields.Integer(required=True, description='ID del curso'),
})
