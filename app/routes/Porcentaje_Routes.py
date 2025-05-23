from ..models.Porcentaje_Model import Porcentaje
from ..schemas.Porcentaje_schema import PorcentajeSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.Porcentaje import ns, porcentaje_model_request, porcentaje_model_response

porcentaje_schema = PorcentajeSchema()
porcentajes_schema = PorcentajeSchema(many=True)

@ns.route('/')
class PorcentajeList(Resource):
    @ns.marshal_list_with(porcentaje_model_response)
    @jwt_required()
    def get(self):
        """Lista todos los porcentajes"""
        porcentajes = Porcentaje.query.all()
        return porcentajes_schema.dump(porcentajes)

    @ns.expect(porcentaje_model_request)
    @ns.marshal_with(porcentaje_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea un nuevo porcentaje"""
        data = request.json
        nuevo_porcentaje = porcentaje_schema.load(data)
        try:
            db.session.add(nuevo_porcentaje)
            db.session.commit()
            return porcentaje_schema.dump(nuevo_porcentaje), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear el porcentaje: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID del porcentaje')
class PorcentajeResource(Resource):
    @ns.marshal_with(porcentaje_model_response)
    @jwt_required()
    def get(self, id):
        """Obtiene un porcentaje por ID"""
        return Porcentaje.query.get_or_404(id)

    @ns.expect(porcentaje_model_request)
    @ns.marshal_with(porcentaje_model_response)
    @jwt_required()
    def put(self, id):
        """Actualiza un porcentaje por ID"""
        porcentaje = Porcentaje.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(porcentaje, key):
                setattr(porcentaje, key, value)

        try:
            db.session.commit()
            return porcentaje_schema.dump(porcentaje)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar el porcentaje: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Elimina un porcentaje por ID"""
        porcentaje = Porcentaje.query.get_or_404(id)
        try:
            db.session.delete(porcentaje)
            db.session.commit()
            return {"message": "Porcentaje eliminado correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar el porcentaje: {str(e)}")
