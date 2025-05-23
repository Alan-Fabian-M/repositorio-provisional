from ..models.Evaluacion_Model import Evaluacion
from ..schemas.Evaluacion_schema import EvaluacionSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.Evaluacion import ns, evaluacion_model_request, evaluacion_model_response

evaluacion_schema = EvaluacionSchema()
evaluaciones_schema = EvaluacionSchema(many=True)

@ns.route('/')
class EvaluacionList(Resource):
    @ns.marshal_list_with(evaluacion_model_response)
    @jwt_required()
    def get(self):
        """Lista todas las evaluaciones"""
        items = Evaluacion.query.all()
        return evaluaciones_schema.dump(items)

    @ns.expect(evaluacion_model_request)
    @ns.marshal_with(evaluacion_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva evaluación"""
        data = request.json
        nueva_evaluacion = evaluacion_schema.load(data)

        try:
            db.session.add(nueva_evaluacion)
            db.session.commit()
            return evaluacion_schema.dump(nueva_evaluacion), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la evaluación: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID de la evaluación')
class EvaluacionResource(Resource):
    @ns.marshal_with(evaluacion_model_response)
    @jwt_required()
    def get(self, id):
        """Obtener una evaluación por ID"""
        return Evaluacion.query.get_or_404(id)

    @ns.expect(evaluacion_model_request)
    @ns.marshal_with(evaluacion_model_response)
    @jwt_required()
    def put(self, id):
        """Actualizar una evaluación por ID"""
        evaluacion = Evaluacion.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(evaluacion, key):
                setattr(evaluacion, key, value)

        try:
            db.session.commit()
            return evaluacion_schema.dump(evaluacion)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Eliminar una evaluación por ID"""
        evaluacion = Evaluacion.query.get_or_404(id)
        try:
            db.session.delete(evaluacion)
            db.session.commit()
            return {"message": "Evaluación eliminada correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar: {str(e)}")


@ns.route('/estudiante/<int:estudiante_ci>')
@ns.param('estudiante_ci', 'CI del estudiante')
class EvaluacionesPorEstudiante(Resource):
    @ns.marshal_list_with(evaluacion_model_response)
    @jwt_required()
    def get(self, estudiante_ci):
        """Buscar evaluaciones por CI del estudiante"""
        evaluaciones = Evaluacion.query.filter_by(estudiante_ci=estudiante_ci).all()
        if not evaluaciones:
            ns.abort(404, f"No se encontraron evaluaciones para el estudiante con CI {estudiante_ci}")
        return evaluaciones_schema.dump(evaluaciones)
