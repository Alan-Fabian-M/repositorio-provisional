from flask_restx import Namespace, Resource, fields

ns = Namespace('Docentes', description='Operaciones relacionadas con docentes')

docente_model_request = ns.model('Docente', {
    'ci': fields.String(required= True, description='carnet de identidad'),
    'nombreCompleto': fields.String(required=True, description='Nombre'),
    'contrasena': fields.String(required=True, description='Contraseña'),
    'gmail': fields.String(required=True, description='gmail'),
    'esDocente': fields.String(description='Es docente'),
})

docente_model_response = ns.model('Docente Response', {
    'ci': fields.String(required= True, description='carnet de identidad'),
    'nombreCompleto': fields.String(required=True, description='Nombre'),
    'gmail': fields.String(required=True, description='gmail'),
    'esDocente': fields.String(description='Es docente'),
})

