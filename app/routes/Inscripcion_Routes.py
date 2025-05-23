from ..models.Inscripcion_Model import Inscripcion
from ..schemas.Inscripcion_schema import InscripcionSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.Inscripcion import ns, inscripcion_model_request, inscripcion_model_response

inscripcion_schema = InscripcionSchema()
inscripciones_schema = InscripcionSchema(many=True)

@ns.route('/')
class InscripcionList(Resource):
    @ns.marshal_list_with(inscripcion_model_response)
    @jwt_required()
    def get(self):
        """Lista todas las inscripciones"""
        inscripciones = Inscripcion.query.all()
        return inscripciones_schema.dump(inscripciones)

    @ns.expect(inscripcion_model_request)
    @ns.marshal_with(inscripcion_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva inscripción"""
        data = request.json
        nueva_inscripcion = inscripcion_schema.load(data)
        try:
            db.session.add(nueva_inscripcion)
            db.session.commit()
            return inscripcion_schema.dump(nueva_inscripcion), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la inscripción: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID de la inscripción')
class InscripcionResource(Resource):
    @ns.marshal_with(inscripcion_model_response)
    @jwt_required()
    def get(self, id):
        """Obtiene una inscripción por ID"""
        return Inscripcion.query.get_or_404(id)

    @ns.expect(inscripcion_model_request)
    @ns.marshal_with(inscripcion_model_response)
    @jwt_required()
    def put(self, id):
        """Actualiza una inscripción por ID"""
        inscripcion = Inscripcion.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(inscripcion, key):
                setattr(inscripcion, key, value)

        try:
            db.session.commit()
            return inscripcion_schema.dump(inscripcion)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar la inscripción: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Elimina una inscripción por ID"""
        inscripcion = Inscripcion.query.get_or_404(id)
        try:
            db.session.delete(inscripcion)
            db.session.commit()
            return {"message": "Inscripción eliminada correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar la inscripción: {str(e)}")
