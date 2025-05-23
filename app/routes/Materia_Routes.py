from ..models.Materia_Model import Materia
from ..schemas.Materia_schema import MateriaSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.Materia import ns, materia_model_request, materia_model_response

materia_schema = MateriaSchema()
materias_schema = MateriaSchema(many=True)

@ns.route('/')
class MateriaList(Resource):
    @ns.marshal_list_with(materia_model_response)
    @jwt_required()
    def get(self):
        """Lista todas las materias"""
        materias = Materia.query.all()
        return materias_schema.dump(materias)

    @ns.expect(materia_model_request)
    @ns.marshal_with(materia_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva materia"""
        data = request.json
        nueva_materia = materia_schema.load(data)
        try:
            db.session.add(nueva_materia)
            db.session.commit()
            return materia_schema.dump(nueva_materia), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la materia: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID de la materia')
class MateriaResource(Resource):
    @ns.marshal_with(materia_model_response)
    @jwt_required()
    def get(self, id):
        """Obtiene una materia por ID"""
        return Materia.query.get_or_404(id)

    @ns.expect(materia_model_request)
    @ns.marshal_with(materia_model_response)
    @jwt_required()
    def put(self, id):
        """Actualiza una materia por ID"""
        materia = Materia.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(materia, key):
                setattr(materia, key, value)

        try:
            db.session.commit()
            return materia_schema.dump(materia)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar la materia: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Elimina una materia por ID"""
        materia = Materia.query.get_or_404(id)
        try:
            db.session.delete(materia)
            db.session.commit()
            return {"message": "Materia eliminada correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar la materia: {str(e)}")
