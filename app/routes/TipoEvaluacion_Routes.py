from ..models.TipoEvaluacion_Model import TipoEvaluacion
from ..schemas.TipoEvaluacion_schema import TipoEvaluacionSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.TipoEvaluacion import ns, tipo_evaluacion_model_request, tipo_evaluacion_model_response

tipo_evaluacion_schema = TipoEvaluacionSchema()
tipo_evaluaciones_schema = TipoEvaluacionSchema(many=True)

@ns.route('/')
class TipoEvaluacionList(Resource):
    @ns.marshal_list_with(tipo_evaluacion_model_response)
    @jwt_required()
    def get(self):
        """Lista todos los tipos de evaluación"""
        tipos = TipoEvaluacion.query.all()
        return tipo_evaluaciones_schema.dump(tipos)

    @ns.expect(tipo_evaluacion_model_request)
    @ns.marshal_with(tipo_evaluacion_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea un nuevo tipo de evaluación"""
        data = request.json
        nuevo_tipo = tipo_evaluacion_schema.load(data)
        try:
            db.session.add(nuevo_tipo)
            db.session.commit()
            return tipo_evaluacion_schema.dump(nuevo_tipo), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear el tipo de evaluación: {str(e)}")

@ns.route('/<int:id>')
@ns.param('id', 'ID del tipo de evaluación')
class TipoEvaluacionResource(Resource):
    @ns.marshal_with(tipo_evaluacion_model_response)
    @jwt_required()
    def get(self, id):
        """Obtiene un tipo de evaluación por ID"""
        return TipoEvaluacion.query.get_or_404(id)

    @ns.expect(tipo_evaluacion_model_request)
    @ns.marshal_with(tipo_evaluacion_model_response)
    @jwt_required()
    def put(self, id):
        """Actualiza un tipo de evaluación por ID"""
        tipo = TipoEvaluacion.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(tipo, key):
                setattr(tipo, key, value)

        try:
            db.session.commit()
            return tipo_evaluacion_schema.dump(tipo)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar el tipo de evaluación: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Elimina un tipo de evaluación por ID"""
        tipo = TipoEvaluacion.query.get_or_404(id)
        try:
            db.session.delete(tipo)
            db.session.commit()
            return {"message": "Tipo de evaluación eliminado correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar el tipo de evaluación: {str(e)}")
