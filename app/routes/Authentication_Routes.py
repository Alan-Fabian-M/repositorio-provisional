from flask_restx import Resource
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
)
from ..models.Docente_Model import Docente
from ..schemas.Docente_schema import DocenteSchema
from werkzeug.security import check_password_hash
from ..api_model.Login import ns, login_model, token_response_model, mensaje_model
from ..api_model.Docente import docente_model_request


usuario_schema = DocenteSchema()
usuarios_schema = DocenteSchema(many = True)

@ns.route('/login')
class Login(Resource):
    @ns.expect(login_model, validate=True)
    @ns.response(200, 'Login exitoso', docente_model_request)
    @ns.response(400, 'Faltan campos')
    @ns.response(401, 'Credenciales inválidas')
    def post(self):
        """Iniciar sesión y obtener token"""
        data = request.get_json()
        gmail = data.get("gmail")
        contrasena = data.get("contrasena")

        usuario = Docente.query.filter_by(gmail=gmail).first()

        if usuario is None:
            ns.abort(401, "Credenciales inválidas")
        
        if not usuario or not check_password_hash(usuario.contrasena, contrasena):
            ns.abort(401, "Credenciales inválidas")
            
        
        token = create_access_token(identity=str(usuario.gmail)) 

        return {"token": token, "Usuario": usuario_schema.dump(usuario)}, 200


@ns.route('/logout')
class Logout(Resource):
    @jwt_required()
    @ns.response(200, 'Logout exitoso', mensaje_model)
    def post(self):
        """Cerrar sesión"""
        response = jsonify({"mensaje": "Logout exitoso"})
        unset_jwt_cookies(response)  # Elimina cookies si las usas
        return response, 200