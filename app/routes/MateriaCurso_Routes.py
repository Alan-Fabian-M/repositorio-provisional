from ..models.MateriaCurso_Model import MateriaCurso
from ..schemas.MateriaCurso_schema import MateriaCursoSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.MateriaCurso import ns, materia_curso_model_request, materia_curso_model_response

materia_curso_schema = MateriaCursoSchema()
materias_curso_schema = MateriaCursoSchema(many=True)

@ns.route('/')
class MateriaCursoList(Resource):
    @ns.marshal_list_with(materia_curso_model_response)
    @jwt_required()
    def get(self):
        """Lista todas las materias asignadas a cursos"""
        materias_curso = MateriaCurso.query.all()
        return materias_curso_schema.dump(materias_curso)

    @ns.expect(materia_curso_model_request)
    @ns.marshal_with(materia_curso_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva asignación de materia a curso"""
        data = request.json
        nueva_asignacion = materia_curso_schema.load(data)
        try:
            db.session.add(nueva_asignacion)
            db.session.commit()
            return materia_curso_schema.dump(nueva_asignacion), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la asignación: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID de la asignación')
class MateriaCursoResource(Resource):
    @ns.marshal_with(materia_curso_model_response)
    @jwt_required()
    def get(self, id):
        """Obtiene una asignación por ID"""
        return MateriaCurso.query.get_or_404(id)

    @ns.expect(materia_curso_model_request)
    @ns.marshal_with(materia_curso_model_response)
    @jwt_required()
    def put(self, id):
        """Actualiza una asignación por ID"""
        asignacion = MateriaCurso.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(asignacion, key):
                setattr(asignacion, key, value)

        try:
            db.session.commit()
            return materia_curso_schema.dump(asignacion)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar la asignación: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Elimina una asignación por ID"""
        asignacion = MateriaCurso.query.get_or_404(id)
        try:
            db.session.delete(asignacion)
            db.session.commit()
            return {"message": "Asignación eliminada correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar la asignación: {str(e)}")
