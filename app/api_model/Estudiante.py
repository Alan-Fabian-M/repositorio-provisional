from flask_restx import Namespace, Resource, fields

ns = Namespace('Estudiantes', description='Operaciones relacionadas con estudiantes')

estudiante_model_request = ns.model('Estudiante', {
    'ci': fields.String(required= True, description='carnet de identidad'),
    'nombreCompleto': fields.String(required=True, description='Nombre'),
    'fechaNacimiento': fields.String(required=True, description='fecha de nacimiento (YYYY-MM-DD)'),
    'contrasena': fields.String(required=True, description='Contraseña'),
    'apoderado': fields.String(description='Nombre del apoderado'),
    'telefono': fields.String(description='Teléfono del apoderado')
})

estudiante_model_response = ns.model('Estudiante Response', {
    'ci': fields.String(required= True, description='carnet de identidad'),
    'nombreCompleto': fields.String(required=True, description='Nombre'),
    'fechaNacimiento': fields.String(required=True, description='fecha de nacimiento (YYYY-MM-DD)'),
    'apoderado': fields.String(description='Nombre del apoderado'),
    'telefono': fields.String(description='Teléfono del apoderado')
})




