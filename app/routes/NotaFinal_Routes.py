from ..models.NotaFinal_Model import NotaFinal
from ..schemas.NotaFinal_schema import NotaFinalSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.NotaFinal import ns, nota_final_model_request, nota_final_model_response

nota_final_schema = NotaFinalSchema()
notas_finales_schema = NotaFinalSchema(many=True)

@ns.route('/')
class NotaFinalList(Resource):
    @ns.marshal_list_with(nota_final_model_response)
    @jwt_required()
    def get(self):
        """Lista todas las notas finales"""
        notas = NotaFinal.query.all()
        return notas_finales_schema.dump(notas)

    @ns.expect(nota_final_model_request)
    @ns.marshal_with(nota_final_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva nota final"""
        data = request.json
        nueva_nota = nota_final_schema.load(data)
        try:
            db.session.add(nueva_nota)
            db.session.commit()
            return nota_final_schema.dump(nueva_nota), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la nota final: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID de la nota final')
class NotaFinalResource(Resource):
    @ns.marshal_with(nota_final_model_response)
    @jwt_required()
    def get(self, id):
        """Obtiene una nota final por ID"""
        return NotaFinal.query.get_or_404(id)

    @ns.expect(nota_final_model_request)
    @ns.marshal_with(nota_final_model_response)
    @jwt_required()
    def put(self, id):
        """Actualiza una nota final por ID"""
        nota = NotaFinal.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(nota, key):
                setattr(nota, key, value)

        try:
            db.session.commit()
            return nota_final_schema.dump(nota)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar la nota final: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Elimina una nota final por ID"""
        nota = NotaFinal.query.get_or_404(id)
        try:
            db.session.delete(nota)
            db.session.commit()
            return {"message": "Nota final eliminada correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar la nota final: {str(e)}")
