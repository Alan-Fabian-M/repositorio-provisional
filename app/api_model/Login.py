from flask_restx import Namespace, Resource, fields

ns = Namespace('auth', description='Autenticación de usuarios')


login_model = ns.model('Login', {
    'gmail': fields.String(required=True, description='Carnet de identidad'),
    'contrasena': fields.String(required=True, description='Contraseña')
})

token_response_model = ns.model('TokenResponse', {
    'token': fields.String(description='Token JWT'),
    'Usuario': fields.String(description='usuario')
})

mensaje_model = ns.model('Mensaje', {
    'mensaje': fields.String
})
