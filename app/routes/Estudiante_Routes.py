from ..models.Estudiante_Model import Estudiante
from ..models.MateriaCurso_Model import MateriaCurso
from ..models.Inscripcion_Model import Inscripcion
from ..models.Evaluacion_Model import Evaluacion
from ..models.EvaluacionIntegral_Model import EvaluacionIntegral
from ..models.TipoEvaluacion_Model import TipoEvaluacion
from ..models.DocenteMateria_Model import DocenteMateria
from ..schemas.Estudiante_schema import EstudianteSchema
from flask import request 
from app import db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.Estudiante import (ns, estudiante_model_request, 
                                   estudiante_model_response,
                                   upload_parser,
                                   estudiante_image_response)
from ..api_model.parsers import upload_parser, estudiante_parser
import cloudinary.uploader
from sqlalchemy import func

estudiante_schema = EstudianteSchema()
estudiantes_schema = EstudianteSchema(many=True)

@ns.route('/')
class EstudianteList(Resource):
    @ns.marshal_with(estudiante_model_response)
    @jwt_required()
    def get(self):
        """Lista todos los estudiantes"""
        estudiantes = Estudiante.query.all()
        return estudiantes_schema.dump(estudiantes)

    @ns.expect(estudiante_parser)
    @ns.marshal_with(estudiante_model_response)
    def post(self):
        """Crea nuevo estudiante con imagen opcional"""
        args = estudiante_parser.parse_args()
        
        # Verificar si el estudiante ya existe
        if Estudiante.query.get(args['ci']):
            ns.abort(400, "Ya existe un estudiante con esta cédula")

        # Crear el estudiante
        nuevo_estudiante = Estudiante(
            nombreCompleto=args['nombreCompleto'],
            ci=args['ci'],
            # contrasena=generate_password_hash(args['contrasena']),
            fechaNacimiento=args['fechaNacimiento'],
            apoderado=args.get('apoderado'),
            telefono=args.get('telefono')
        )

        # Manejar la imagen si fue enviada
        if args['file']:
            try:
                # print("Cloudinary config:", {
                # 'cloud_name': cloudinary.config().cloud_name,
                # 'api_key': cloudinary.config().api_key
                # }) 
                upload_result = cloudinary.uploader.upload(args['file'])
                nuevo_estudiante.imagen_url = upload_result['secure_url']
                nuevo_estudiante.imagen_public_id = upload_result['public_id']
            except Exception as e:
                ns.abort(500, f"Error al subir imagen: {str(e)}")

        try:
            db.session.add(nuevo_estudiante)
            db.session.commit()
            return estudiante_schema.dump(nuevo_estudiante), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear estudiante: {str(e)}")


@ns.route('/<int:ci>')
@ns.param('ci', 'Ci del estudiante')
class EstudianteResource(Resource):
    @ns.marshal_with(estudiante_model_response)
    @jwt_required()
    def get(self, ci):
        """Obtener estudiante por código"""
        # estudiante = Estudiante.query.get_or_404(ci)
        return Estudiante.query.get_or_404(ci)

    @jwt_required()
    @ns.expect(estudiante_model_request)
    @ns.marshal_with(estudiante_model_response)
    def put(self, ci):
        """Actualizar estudiante por código"""
        estudiante = Estudiante.query.get_or_404(ci)
        data = request.json

        if 'contrasena' in data:
            data['contrasena'] = generate_password_hash(data['contrasena'])
        
        # No permitir actualización directa de imagen_url o public_id
        if 'imagen_url' in data or 'imagen_public_id' in data:
            ns.abort(400, 'Use el endpoint /upload-image para actualizar imágenes')

        for key, value in data.items():
            if hasattr(estudiante, key):
                setattr(estudiante, key, value)

        try:
            db.session.commit()
            return estudiante_schema.dump(estudiante)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar: {str(e)}")

    @jwt_required()
    def delete(self, ci):
        """Eliminar estudiante por código"""
        estudiante = Estudiante.query.get_or_404(ci)
        try:
            db.session.delete(estudiante)
            db.session.commit()
            return {"message": "Estudiante eliminado correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar: {str(e)}")


@ns.route('/buscar/<string:nombreCompleto>')
@ns.param('nombreCompleto', 'Nombre a buscar')
class EstudianteBuscar(Resource):
    @jwt_required()
    @ns.marshal_list_with(estudiante_model_response)
    def get(self, nombreCompleto):
        """Buscar estudiante por nombre"""
        estudiantes = Estudiante.query.filter(Estudiante.nombreCompleto.ilike(f"%{nombreCompleto}%")).all()
        if not estudiantes:
            ns.abort(404, f"No se encontraron estudiantes con nombre '{nombreCompleto}'")
        return estudiantes_schema.dump(estudiantes)


@ns.route('/<int:ci>/upload-image')
@ns.response(404, 'Estudiante no encontrado')
class EstudianteImageUpload(Resource):
    @ns.doc(security='Bearer')
    @jwt_required()
    @ns.expect(upload_parser)
    @ns.marshal_with(estudiante_image_response)
    def put(self, ci):
        """Sube/actualiza la imagen de un estudiante"""
        estudiante = Estudiante.query.get_or_404(ci)
        args = upload_parser.parse_args()
        file = args['file']
        
        # Si ya tiene una imagen, la eliminamos de Cloudinary primero
        if estudiante.imagen_public_id:
            try:
                cloudinary.uploader.destroy(estudiante.imagen_public_id)
            except:
                pass  # Si falla, continuamos igual
        
        # Subir nueva imagen
        try:
            upload_result = cloudinary.uploader.upload(file)
            estudiante.imagen_url = upload_result.get('secure_url')
            estudiante.imagen_public_id = upload_result.get('public_id')
            db.session.commit()
            
            return {
                'ci': estudiante.ci,
                'nombreCompleto': estudiante.nombreCompleto,
                'imagen_url': estudiante.imagen_url,
                'message': 'Imagen actualizada correctamente'
            }
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al subir la imagen: {str(e)}")

@ns.route('/<int:ci>/delete-image')
@ns.response(404, 'Estudiante no encontrado')
class EstudianteImageDelete(Resource):
    @ns.doc(security='Bearer')
    @jwt_required()
    @ns.marshal_with(estudiante_image_response)
    def delete(self, ci):
        """Elimina la imagen de un estudiante"""
        estudiante = Estudiante.query.get_or_404(ci)
        
        if not estudiante.imagen_public_id:
            ns.abort(400, 'El estudiante no tiene imagen asociada')
            
        try:
            cloudinary.uploader.destroy(estudiante.imagen_public_id)
            estudiante.imagen_url = None
            estudiante.imagen_public_id = None
            db.session.commit()
            
            return {
                'ci': estudiante.ci,
                'nombreCompleto': estudiante.nombreCompleto,
                'imagen_url': None,
                'message': 'Imagen eliminada correctamente'
            }
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar la imagen: {str(e)}")
            
@ns.route('/filtrar-estudiantes')
class EstudiantesFiltrados(Resource):
    @jwt_required()
    @ns.doc(params={
        'docente_ci': 'CI del docente',
        'materia_id': 'ID de la materia',
        'curso_id': 'ID del curso'
    })
    def get(self):
        """Filtra estudiantes por docente, materia y curso"""
        docente_ci = request.args.get('docente_ci', type=int)
        materia_id = request.args.get('materia_id', type=int)
        curso_id = request.args.get('curso_id', type=int)

        if not all([docente_ci, materia_id, curso_id]):
            return {'message': 'Faltan parámetros'}, 400

        # Subconsulta para validar que ese docente da esa materia
        dm = DocenteMateria.query.filter_by(
            docente_ci=docente_ci,
            materia_id=materia_id
        ).first()

        if not dm:
            return {'message': 'El docente no enseña esa materia'}, 404

        # Verificar que la materia esté en ese curso
        mc = MateriaCurso.query.filter_by(
            materia_id=materia_id,
            curso_id=curso_id
        ).first()

        if not mc:
            return {'message': 'La materia no pertenece a ese curso'}, 404

        # Buscar inscripciones al curso
        inscripciones = Inscripcion.query.filter_by(curso_id=curso_id).all()

        estudiantes = [ins.estudiante for ins in inscripciones]

        return estudiantes_schema.dump(estudiantes), 200



