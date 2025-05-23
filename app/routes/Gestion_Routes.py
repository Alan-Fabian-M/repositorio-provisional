from ..models.Gestion_Model import Gestion
from ..schemas.Gestion_schema import GestionSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.Gestion import ns, gestion_model_request, gestion_model_response

gestion_schema = GestionSchema()
gestiones_schema = GestionSchema(many=True)

@ns.route('/')
class GestionList(Resource):
    @ns.marshal_list_with(gestion_model_response)
    @jwt_required()
    def get(self):
        """Lista todas las gestiones"""
        gestiones = Gestion.query.all()
        return gestiones_schema.dump(gestiones)

    @ns.expect(gestion_model_request)
    @ns.marshal_with(gestion_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva gestión"""
        data = request.json
        nueva_gestion = gestion_schema.load(data)
        try:
            db.session.add(nueva_gestion)
            db.session.commit()
            return gestion_schema.dump(nueva_gestion), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la gestión: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID de la gestión')
class GestionResource(Resource):
    @ns.marshal_with(gestion_model_response)
    @jwt_required()
    def get(self, id):
        """Obtiene una gestión por ID"""
        return Gestion.query.get_or_404(id)

    @ns.expect(gestion_model_request)
    @ns.marshal_with(gestion_model_response)
    @jwt_required()
    def put(self, id):
        """Actualiza una gestión por ID"""
        gestion = Gestion.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(gestion, key):
                setattr(gestion, key, value)

        try:
            db.session.commit()
            return gestion_schema.dump(gestion)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar la gestión: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Elimina una gestión por ID"""
        gestion = Gestion.query.get_or_404(id)
        try:
            db.session.delete(gestion)
            db.session.commit()
            return {"message": "Gestión eliminada correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar la gestión: {str(e)}")
