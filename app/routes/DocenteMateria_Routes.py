from ..models.DocenteMateria_Model import DocenteMateria
from ..schemas.DocenteMateria_schema import DocenteMateriaSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.DocenteMateria import ns, docente_materia_model_request, docente_materia_mode_response

docente_materia_schema = DocenteMateriaSchema()
docentes_materias_schema = DocenteMateriaSchema(many=True)

@ns.route('/')
class DocenteMateriaList(Resource):
    @ns.marshal_list_with(docente_materia_mode_response)
    @jwt_required()
    def get(self):
        """Lista todas las asignaciones de docente a materia"""
        items = DocenteMateria.query.all()
        return docentes_materias_schema.dump(items)

    @ns.expect(docente_materia_model_request)
    @ns.marshal_with(docente_materia_mode_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva asignación de docente a materia"""
        data = request.json
        nueva_asignacion = docente_materia_schema.load(data)

        try:
            db.session.add(nueva_asignacion)
            db.session.commit()
            return docente_materia_schema.dump(nueva_asignacion), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la asignación: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID de la asignación docente-materia')
class DocenteMateriaResource(Resource):
    @ns.marshal_with(docente_materia_mode_response)
    @jwt_required()
    def get(self, id):
        """Obtener una asignación por ID"""
        return DocenteMateria.query.get_or_404(id)

    @ns.expect(docente_materia_model_request)
    @ns.marshal_with(docente_materia_mode_response)
    @jwt_required()
    def put(self, id):
        """Actualizar una asignación por ID"""
        asignacion = DocenteMateria.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(asignacion, key):
                setattr(asignacion, key, value)

        try:
            db.session.commit()
            return docente_materia_schema.dump(asignacion)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Eliminar una asignación por ID"""
        asignacion = DocenteMateria.query.get_or_404(id)
        try:
            db.session.delete(asignacion)
            db.session.commit()
            return {"message": "Asignación eliminada correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar: {str(e)}")


@ns.route('/buscar/<int:docente_ci>')
@ns.param('docente_ci', 'CI del docente')
class BuscarPorDocente(Resource):
    @ns.marshal_list_with(docente_materia_mode_response)
    @jwt_required()
    def get(self, docente_ci):
        """Buscar asignaciones por CI del docente"""
        asignaciones = DocenteMateria.query.filter_by(docente_ci=docente_ci).all()
        if not asignaciones:
            ns.abort(404, f"No se encontraron asignaciones para el docente con CI {docente_ci}")
        return docentes_materias_schema.dump(asignaciones)
