from ..models.Curso_Model import Curso
from ..models.Docente_Model import Docente
from ..models.MateriaCurso_Model import MateriaCurso
from ..models.DocenteMateria_Model import DocenteMateria
from ..schemas.Curso_schema import CursoSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.Curso import ns, curso_model_request, curso_model_response

curso_schema = CursoSchema()
cursos_schema = CursoSchema(many=True)

@ns.route('/')
class CursoList(Resource):
    @ns.marshal_list_with(curso_model_response)
    @jwt_required()
    def get(self):
        """Lista todos los cursos"""
        cursos = Curso.query.all()
        return cursos_schema.dump(cursos)

    @ns.expect(curso_model_request)
    @ns.marshal_with(curso_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea un nuevo curso"""
        data = request.json

        if 'nombre' not in data:
            ns.abort(400, "El campo 'nombre' es requerido")

        nuevo_curso = curso_schema.load(data)

        try:
            db.session.add(nuevo_curso)
            db.session.commit()
            return curso_schema.dump(nuevo_curso), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear el curso: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID del curso')
class CursoResource(Resource):
    @ns.marshal_with(curso_model_response)
    @jwt_required()
    def get(self, id):
        """Obtener curso por ID"""
        return Curso.query.get_or_404(id)

    @ns.expect(curso_model_request)
    @ns.marshal_with(curso_model_response)
    @jwt_required()
    def put(self, id):
        """Actualizar curso por ID"""
        curso = Curso.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(curso, key):
                setattr(curso, key, value)

        try:
            db.session.commit()
            return curso_schema.dump(curso)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Eliminar curso por ID"""
        curso = Curso.query.get_or_404(id)
        try:
            db.session.delete(curso)
            db.session.commit()
            return {"message": "Curso eliminado correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar: {str(e)}")


@ns.route('/buscar/<string:nombre>')
@ns.param('nombre', 'Nombre a buscar')
class CursoBuscar(Resource):
    @ns.marshal_list_with(curso_model_response)
    @jwt_required()
    def get(self, nombre):
        """Buscar curso por nombre"""
        cursos = Curso.query.filter(Curso.nombre.ilike(f"%{nombre}%")).all()
        if not cursos:
            ns.abort(404, f"No se encontraron cursos con nombre '{nombre}'")
        return cursos_schema.dump(cursos)

@ns.route('/CursoDocente/<int:docente_ci>')
@ns.param('docente_ci', 'Cursos a buscar por Ci docente')
class CursoBuscarXDocenteCi(Resource):
    @ns.marshal_list_with(curso_model_response)
    @jwt_required()
    def get(self, docente_ci):
        docente = Docente.query.get(docente_ci)
        if not docente:
            return {'mensaje': 'Docente no encontrado'}, 404

        cursos = db.session.query(Curso)\
            .join(MateriaCurso, Curso.id == MateriaCurso.curso_id)\
            .join(DocenteMateria, 
                  (MateriaCurso.materia_id == DocenteMateria.materia_id) & 
                  (DocenteMateria.docente_ci == docente_ci))\
            .distinct().all()

        if not cursos:
            return {'mensaje': 'El docente no tiene cursos asignados'}, 404

        return cursos_schema.dump(list(cursos)), 200
