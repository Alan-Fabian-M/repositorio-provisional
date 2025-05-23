from flask_restx import Namespace, Resource, fields

ns = Namespace('Materias', description='Operaciones relacionadas con materia')

materia_model_request = ns.model('Materia', {
    'nombre': fields.String(required=True, description='Nombre de la materia'),
    'descripcion': fields.String(description='Descripción'),
    'codigo': fields.String(required=True, description='Código único'),
})

materia_model_response = ns.inherit('Materia Response', materia_model_request, {
    'id': fields.Integer(description='ID de la materia'),
})
