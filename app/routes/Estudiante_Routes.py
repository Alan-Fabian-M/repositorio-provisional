from ..models.Estudiante_Model import Estudiante
from ..schemas.Estudiante_schema import EstudianteSchema
from flask import request 
from app import db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.Estudiante import ns, estudiante_model_request, estudiante_model_response
from datetime import datetime



estudiante_schema = EstudianteSchema()
estudiantes_schema = EstudianteSchema(many=True)

@ns.route('/')
class EstudianteList(Resource):
    @ns.marshal_with(estudiante_model_response)
    @jwt_required()
    def get(self):
        """Lista todos los estudiantes"""
        estudiantes = Estudiante.query.all()
        return estudiantes_schema.dump(estudiantes)

    @ns.marshal_with(estudiante_model_response)
    @ns.expect(estudiante_model_request)
    def post(self):
        """Crea un nuevo estudiante"""
        data = request.json

        required_fields = ['nombreCompleto', 'ci', 'contrasena']
        for field in required_fields:
            if field not in data:
                ns.abort(400, f"El campo '{field}' es requerido")

        data['contrasena'] = generate_password_hash(data['contrasena'])
        nuevo_estudiante = estudiante_schema.load(data)

        try:
            db.session.add(nuevo_estudiante)
            db.session.commit()
            return estudiante_schema.dump(nuevo_estudiante), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear el estudiante: {str(e)}")


@ns.route('/<int:ci>')
@ns.param('ci', 'Ci del estudiante')
class EstudianteResource(Resource):
    @ns.marshal_with(estudiante_model_response)
    @jwt_required()
    def get(self, ci):
        """Obtener estudiante por código"""
        # estudiante = Estudiante.query.get_or_404(ci)
        return Estudiante.query.get_or_404(ci)

    @jwt_required()
    @ns.expect(estudiante_model_request)
    @ns.marshal_with(estudiante_model_response)
    def put(self, ci):
        """Actualizar estudiante por código"""
        estudiante = Estudiante.query.get_or_404(ci)
        data = request.json

        if 'contrasena' in data:
            data['contrasena'] = generate_password_hash(data['contrasena'])

        for key, value in data.items():
            if hasattr(estudiante, key):
                setattr(estudiante, key, value)

        try:
            db.session.commit()
            return estudiante_schema.dump(estudiante)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar: {str(e)}")
            
        return Estudiante.query.get_or_404(ci)

    @jwt_required()
    def delete(self, ci):
        """Eliminar estudiante por código"""
        estudiante = Estudiante.query.get_or_404(ci)
        try:
            db.session.delete(estudiante)
            db.session.commit()
            return {"message": "Estudiante eliminado correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar: {str(e)}")


@ns.route('/buscar/<string:nombreCompleto>')
@ns.param('nombreCompleto', 'Nombre a buscar')
class EstudianteBuscar(Resource):
    @jwt_required()
    @ns.marshal_list_with(estudiante_model_response)
    def get(self, nombreCompleto):
        """Buscar estudiante por nombre"""
        estudiantes = Estudiante.query.filter(Estudiante.nombreCompleto.ilike(f"%{nombreCompleto}%")).all()
        if not estudiantes:
            ns.abort(404, f"No se encontraron estudiantes con nombre '{nombreCompleto}'")
        return estudiantes_schema.dump(estudiantes)


# @ns.route('/validar-correo')
# class ValidarCorreo(Resource):
#     @ns.doc(params={'gmail': 'Correo a validar'})
#     def post(self):
#         """Validar si un correo ya existe"""
#         gmail = request.json.get('gmail')
#         if not gmail:
#             ns.abort(400, "Correo no proporcionado")

#         existe = Estudiante.query.filter_by(gmail=gmail).first() is not None
#         return {"existe": existe}