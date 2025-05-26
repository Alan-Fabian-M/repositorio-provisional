from ..models.EvaluacionIntegral_Model import EvaluacionIntegral
from ..schemas.EvaluacionIntegral_schema import EvaluacionIntegralSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.EvalaucionIntegral import ns, EvaluacionIntegral_model_request, EvaluacionIntegral_model_response

evaluacionIntegral_schema = EvaluacionIntegralSchema()
evaluacionIntegrales_schema = EvaluacionIntegralSchema(many=True)

@ns.route('/')
class EvaluacionIntegralList(Resource):
    @ns.marshal_list_with(EvaluacionIntegral_model_response)
    @jwt_required()
    def get(self):
        """Lista todos las evaluaciones Integrales"""
        evaluacionesIntegrales = EvaluacionIntegral.query.all()
        return evaluacionIntegrales_schema.dump(evaluacionesIntegrales)

    @ns.expect(EvaluacionIntegral_model_request)
    @ns.marshal_with(EvaluacionIntegral_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea un nueva evaluacion Integral"""
        data = request.json
        nueva_evaluacionIntegral = evaluacionIntegral_schema.load(data)
        try:
            db.session.add(nueva_evaluacionIntegral)
            db.session.commit()
            return evaluacionIntegral_schema.dump(nueva_evaluacionIntegral), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la evaluacion Integral: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID del evaluacionIntegral')
class EvaluacionIntegralResource(Resource):
    @ns.marshal_with(EvaluacionIntegral_model_response)
    @jwt_required()
    def get(self, id):
        """Obtiene una evaluacionIntegral por ID"""
        return EvaluacionIntegral.query.get_or_404(id)

    @ns.expect(EvaluacionIntegral_model_request)
    @ns.marshal_with(EvaluacionIntegral_model_response)
    @jwt_required()
    def put(self, id):
        """Actualiza una evaluacionIntegral por ID"""
        evaluacionIntegral = EvaluacionIntegral.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(evaluacionIntegral, key):
                setattr(evaluacionIntegral, key, value)

        try:
            db.session.commit()
            return evaluacionIntegral_schema.dump(evaluacionIntegral)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar la evaluacion Integral: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Elimina un evaluacionIntegral por ID"""
        evaluacionIntegral = EvaluacionIntegral.query.get_or_404(id)
        try:
            db.session.delete(evaluacionIntegral)
            db.session.commit()
            return {"message": "evaluacion Integral eliminado correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar la evaluacion Integral: {str(e)}")
