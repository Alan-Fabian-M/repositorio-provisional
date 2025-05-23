from ..models.NotaEstimada_Model import NotaEstimada
from ..schemas.NotaEstimada_schema import NotaEstimadaSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.NotaEstimada import ns, nota_estimada_model_request, nota_estimada_model_response

nota_estimada_schema = NotaEstimadaSchema()
notas_estimadas_schema = NotaEstimadaSchema(many=True)

@ns.route('/')
class NotaEstimadaList(Resource):
    @ns.marshal_list_with(nota_estimada_model_response)
    @jwt_required()
    def get(self):
        """Lista todas las notas estimadas"""
        notas = NotaEstimada.query.all()
        return notas_estimadas_schema.dump(notas)

    @ns.expect(nota_estimada_model_request)
    @ns.marshal_with(nota_estimada_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva nota estimada"""
        data = request.json
        nueva_nota = nota_estimada_schema.load(data)
        try:
            db.session.add(nueva_nota)
            db.session.commit()
            return nota_estimada_schema.dump(nueva_nota), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la nota estimada: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID de la nota estimada')
class NotaEstimadaResource(Resource):
    @ns.marshal_with(nota_estimada_model_response)
    @jwt_required()
    def get(self, id):
        """Obtiene una nota estimada por ID"""
        return NotaEstimada.query.get_or_404(id)

    @ns.expect(nota_estimada_model_request)
    @ns.marshal_with(nota_estimada_model_response)
    @jwt_required()
    def put(self, id):
        """Actualiza una nota estimada por ID"""
        nota = NotaEstimada.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(nota, key):
                setattr(nota, key, value)

        try:
            db.session.commit()
            return nota_estimada_schema.dump(nota)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar la nota estimada: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Elimina una nota estimada por ID"""
        nota = NotaEstimada.query.get_or_404(id)
        try:
            db.session.delete(nota)
            db.session.commit()
            return {"message": "Nota estimada eliminada correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar la nota estimada: {str(e)}")
