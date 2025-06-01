from ..models.Docente_Model import Docente
from ..models.DocenteMateria_Model import DocenteMateria
from ..models.MateriaCurso_Model import MateriaCurso
from ..models.Materia_Model import Materia
from ..models.Curso_Model import Curso
from ..schemas.Docente_schema import  DocenteSchema
from ..schemas.Materia_schema import MateriaSchema
from flask import request 
from app import db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.Docente import ns, docente_model_request, docente_model_response
from ..api_model.Materia import materia_model_response
from datetime import datetime



docente_schema = DocenteSchema()
docentes_schema = DocenteSchema(many=True)
materia_schema = MateriaSchema()
materias_schema = MateriaSchema(many=True)

@ns.route('/')
class DocenteList(Resource):
    @ns.marshal_with(docente_model_response)
    @jwt_required()
    def get(self):
        """Lista todos los docentes"""
        docentes = Docente.query.all()
        return docentes_schema.dump(docentes)

    @ns.marshal_with(docente_model_response)
    @ns.expect(docente_model_request)
    def post(self):
        """Crea un nuevo docente"""
        data = request.json

        required_fields = ['nombreCompleto', 'ci', 'contrasena']
        for field in required_fields:
            if field not in data:
                ns.abort(400, f"El campo '{field}' es requerido")

        data['contrasena'] = generate_password_hash(data['contrasena'])
        nuevo_docente = docente_schema.load(data)

        try:
            db.session.add(nuevo_docente)
            db.session.commit()
            return docente_schema.dump(nuevo_docente), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear el docente: {str(e)}")


@ns.route('/<int:ci>')
@ns.param('ci', 'Ci del docente')
class DocenteResource(Resource):
    @ns.marshal_with(docente_model_response)
    @jwt_required()
    def get(self, ci):
        """Obtener docente por código"""
        # docente = docente.query.get_or_404(ci)
        return Docente.query.get_or_404(ci)

    @jwt_required()
    @ns.expect(docente_model_request)
    @ns.marshal_with(docente_model_response)
    def put(self, ci):
        """Actualizar docente por código"""
        docente = Docente.query.get_or_404(ci)
        data = request.json

        if 'contrasena' in data:
            data['contrasena'] = generate_password_hash(data['contrasena'])

        for key, value in data.items():
            if hasattr(docente, key):
                setattr(docente, key, value)

        try:
            db.session.commit()
            return docente_schema.dump(docente)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar: {str(e)}")
            
        return Docente.query.get_or_404(ci)

    @jwt_required()
    def delete(self, ci):
        """Eliminar docente por código"""
        docente = Docente.query.get_or_404(ci)
        try:
            db.session.delete(docente)
            db.session.commit()
            return {"message": "Docente eliminado correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar: {str(e)}")


@ns.route('/buscar/<string:nombreCompleto>')
@ns.param('nombreCompleto', 'Nombre a buscar')
class DocenteBuscar(Resource):
    @jwt_required()
    @ns.marshal_list_with(docente_model_response)
    def get(self, nombreCompleto):
        """Buscar docente por nombre"""
        docentes = Docente.query.filter(Docente.nombreCompleto.ilike(f"%{nombreCompleto}%")).all()
        if not docentes:
            ns.abort(404, f"No se encontraron docente con nombre '{nombreCompleto}'")
        return docentes_schema.dump(docentes)


@ns.route('/<int:ci>/curso/<int:curso_id>/materias')
@ns.param('ci', 'CI del docente')
@ns.param('curso_id', 'ID del curso')
class DocenteMateriasEnCurso(Resource):
    @jwt_required()
    @ns.marshal_list_with(materia_model_response)
    def get(self, ci, curso_id):
        """Obtener las materias que un docente enseña en un curso específico"""
        # Verificar que el docente existe
        docente = Docente.query.get_or_404(ci)
        
        # Verificar que el curso existe
        curso = Curso.query.get_or_404(curso_id)
        
        # Consulta para obtener las materias que el docente enseña en el curso específico
        materias = db.session.query(Materia)\
            .join(DocenteMateria, Materia.id == DocenteMateria.materia_id)\
            .join(MateriaCurso, Materia.id == MateriaCurso.materia_id)\
            .filter(
                DocenteMateria.docente_ci == ci,
                MateriaCurso.curso_id == curso_id
            ).all()
        
        if not materias:
            ns.abort(404, f"El docente con CI {ci} no tiene materias asignadas en el curso {curso.nombre}")
        
        return materias_schema.dump(materias)


# @ns.route('/validar-correo')
# class ValidarCorreo(Resource):
#     @ns.doc(params={'gmail': 'Correo a validar'})
#     def post(self):
#         """Validar si un correo ya existe"""
#         gmail = request.json.get('gmail')
#         if not gmail:
#             ns.abort(400, "Correo no proporcionado")

#         existe = Docente.query.filter_by(gmail=gmail).first() is not None
#         return {"existe": existe}