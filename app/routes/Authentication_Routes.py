from flask_restx import Resource
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
)
from ..models.Estudiante_Model import Estudiante
from ..schemas.Estudiante_schema import EstudianteSchema
from werkzeug.security import check_password_hash
from ..api_model.Login import ns, login_model, token_response_model, mensaje_model
from ..api_model.Estudiante import estudiante_model_request


usuario_schema = EstudianteSchema()
usuarios_schema = EstudianteSchema(many = True)

@ns.route('/login')
class Login(Resource):
    @ns.expect(login_model, validate=True)
    @ns.response(200, 'Login exitoso', estudiante_model_request)
    @ns.response(400, 'Faltan campos')
    @ns.response(401, 'Credenciales inválidas')
    def post(self):
        """Iniciar sesión y obtener token"""
        data = request.get_json()
        ci = data.get("ci")
        contrasena = data.get("contrasena")

        usuario = Estudiante.query.filter_by(ci=ci).first()

        if usuario is None:
            ns.abort(401, "Credenciales inválidas")
        
        if not usuario or not check_password_hash(usuario.contrasena, contrasena):
            ns.abort(401, "Credenciales inválidas")
            
        
        token = create_access_token(identity=str(usuario.ci)) 

        return {"token": token, "Usuario": usuario_schema.dump(usuario)}, 200


# @ns.route('/verificar-token')
# class VerificarToken(Resource):
#     @jwt_required()
#     @ns.response(200, 'Token válido', estudiante_model_request)
#     def get(self):
#         """Verifica si el token actual es válido"""
#         usuario_id = get_jwt_identity()
#         usuario = Estudiante.query.get(usuario_id)

#         if not usuario:
#             ns.abort(404, "Usuario no encontrado")

#         return usuario_schema.dump(usuario), 200


@ns.route('/logout')
class Logout(Resource):
    @jwt_required()
    @ns.response(200, 'Logout exitoso', mensaje_model)
    def post(self):
        """Cerrar sesión"""
        response = jsonify({"mensaje": "Logout exitoso"})
        unset_jwt_cookies(response)  # Elimina cookies si las usas
        return response, 200