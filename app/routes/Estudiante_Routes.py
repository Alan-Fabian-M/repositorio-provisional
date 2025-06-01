from ..models.Estudiante_Model import Estudiante
from ..models.MateriaCurso_Model import MateriaCurso
from ..models.Inscripcion_Model import Inscripcion
from ..models.Evaluacion_Model import Evaluacion
from ..models.EvaluacionIntegral_Model import EvaluacionIntegral
from ..models.TipoEvaluacion_Model import TipoEvaluacion
from ..models.DocenteMateria_Model import DocenteMateria
from ..models.Docente_Model import Docente
from ..models.Materia_Model import Materia
from ..models.Curso_Model import Curso
from ..models.NotaFinal_Model import NotaFinal
from ..models.NotaEstimada_Model import NotaEstimada
from ..models.Gestion_Model import Gestion
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
        'curso_id': 'ID del curso',
        'year': 'Año de inscripción (opcional, por defecto 2025)'
    })
    @ns.marshal_list_with(estudiante_model_response)
    def get(self):
        """Filtra estudiantes por docente, materia y curso para un año específico"""
        try:
            docente_ci = request.args.get('docente_ci', type=int)
            materia_id = request.args.get('materia_id', type=int)
            curso_id = request.args.get('curso_id', type=int)
            year = request.args.get('year', type=int, default=2025)

            # Validar parámetros requeridos
            if not all([docente_ci, materia_id, curso_id]):
                ns.abort(400, 'Faltan parámetros requeridos: docente_ci, materia_id, curso_id')            # Validar que el docente existe
            docente = Docente.query.filter_by(ci=docente_ci).first()
            if not docente:
                ns.abort(404, 'Docente no encontrado')

            # Validar que la materia existe
            materia = Materia.query.get(materia_id)
            if not materia:
                ns.abort(404, 'Materia no encontrada')

            # Validar que el curso existe
            curso = Curso.query.get(curso_id)
            if not curso:
                ns.abort(404, 'Curso no encontrado')

            # Validar que el docente enseña esa materia
            dm = DocenteMateria.query.filter_by(
                docente_ci=docente_ci,
                materia_id=materia_id
            ).first()

            if not dm:
                ns.abort(404, 'El docente no enseña esa materia')

            # Verificar que la materia pertenece a ese curso
            mc = MateriaCurso.query.filter_by(
                materia_id=materia_id,
                curso_id=curso_id
            ).first()

            if not mc:
                ns.abort(404, 'La materia no pertenece a ese curso')

            # Buscar inscripciones al curso del año especificado
            inscripciones = Inscripcion.query.filter(
                Inscripcion.curso_id == curso_id,
                func.extract('year', Inscripcion.fecha) == year
            ).all()

            # Extraer estudiantes únicos de las inscripciones
            estudiantes = list({ins.estudiante.ci: ins.estudiante for ins in inscripciones}.values())

            return estudiantes_schema.dump(estudiantes), 200

        except Exception as e:
            ns.abort(500, f'Error interno del servidor: {str(e)}')


@ns.route('/boletin-estudiantes-filtrados')
class BoletinEstudiantesFiltrados(Resource):
    @jwt_required()
    @ns.doc(params={
        'docente_ci': 'CI del docente',
        'materia_id': 'ID de la materia',
        'curso_id': 'ID del curso',
        'year': 'Año de inscripción (opcional, por defecto 2025)'
    })
    def get(self):
        """Genera boletín de estudiantes filtrados con notas finales por períodos para una materia específica"""
        try:
            docente_ci = request.args.get('docente_ci', type=int)
            materia_id = request.args.get('materia_id', type=int)
            curso_id = request.args.get('curso_id', type=int)
            year = request.args.get('year', type=int, default=2025)

            # Validar parámetros requeridos
            if not all([docente_ci, materia_id, curso_id]):
                ns.abort(400, 'Faltan parámetros requeridos: docente_ci, materia_id, curso_id')

            # Validar que el docente existe
            docente = Docente.query.filter_by(ci=docente_ci).first()
            if not docente:
                ns.abort(404, 'Docente no encontrado')

            # Validar que la materia existe
            materia = Materia.query.get(materia_id)
            if not materia:
                ns.abort(404, 'Materia no encontrada')

            # Validar que el curso existe
            curso = Curso.query.get(curso_id)
            if not curso:
                ns.abort(404, 'Curso no encontrado')

            # Validar que el docente enseña esa materia
            dm = DocenteMateria.query.filter_by(
                docente_ci=docente_ci,
                materia_id=materia_id
            ).first()

            if not dm:
                ns.abort(404, 'El docente no enseña esa materia')

            # Verificar que la materia pertenece a ese curso
            mc = MateriaCurso.query.filter_by(
                materia_id=materia_id,
                curso_id=curso_id
            ).first()

            if not mc:
                ns.abort(404, 'La materia no pertenece a ese curso')

            # Buscar inscripciones al curso del año especificado
            inscripciones = Inscripcion.query.filter(
                Inscripcion.curso_id == curso_id,
                func.extract('year', Inscripcion.fecha) == year
            ).all()

            # Extraer estudiantes únicos de las inscripciones
            estudiantes = list({ins.estudiante.ci: ins.estudiante for ins in inscripciones}.values())

            if not estudiantes:
                return {
                    'mensaje': 'No se encontraron estudiantes para los criterios especificados',
                    'filtros_aplicados': {
                        'docente_ci': docente_ci,
                        'materia_id': materia_id,
                        'curso_id': curso_id,
                        'year': year
                    },
                    'estudiantes': [],
                    'resumen': {}
                }, 200

            # Obtener todas las gestiones del año especificado
            gestiones = Gestion.query.filter_by(anio=year).all()
            
            if not gestiones:
                return {
                    'mensaje': f'No se encontraron gestiones para el año {year}',
                    'estudiantes': estudiantes_schema.dump(estudiantes),
                    'resumen': {}
                }, 200

            # Construir el boletín para cada estudiante
            boletin_resultado = []
            
            for estudiante in estudiantes:
                estudiante_boletin = {
                    'ci': estudiante.ci,
                    'nombreCompleto': estudiante.nombreCompleto,
                    'materia': {
                        'id': materia.id,
                        'nombre': materia.nombre,
                        'descripcion': materia.descripcion
                    },
                    'periodos': [],
                    'promedio_total': 0.0,
                    'total_periodos': 0
                }
                
                notas_por_periodo = []
                
                # Para cada gestión (período), obtener la nota final
                for gestion in gestiones:
                    nota_final = NotaFinal.query.filter_by(
                        estudiante_ci=estudiante.ci,
                        materia_id=materia_id,
                        gestion_id=gestion.id
                    ).first()
                    
                    periodo_info = {
                        'gestion_id': gestion.id,
                        'periodo': gestion.periodo,
                        'anio': gestion.anio,
                        'nota_final': nota_final.valor if nota_final else 0.0,
                        'tiene_nota': nota_final is not None
                    }
                    
                    estudiante_boletin['periodos'].append(periodo_info)
                    
                    if nota_final:
                        notas_por_periodo.append(nota_final.valor)
                
                # Calcular promedio total
                if notas_por_periodo:
                    estudiante_boletin['promedio_total'] = round(sum(notas_por_periodo) / len(notas_por_periodo), 2)
                    estudiante_boletin['total_periodos'] = len(notas_por_periodo)
                
                boletin_resultado.append(estudiante_boletin)
            
            # Calcular resumen general
            total_estudiantes = len(estudiantes)
            total_gestiones = len(gestiones)
            
            resumen = {
                'total_estudiantes': total_estudiantes,
                'total_periodos_disponibles': total_gestiones,
                'materia_info': {
                    'id': materia.id,
                    'nombre': materia.nombre,
                    'descripcion': materia.descripcion
                },
                'curso_info': {
                    'id': curso.id,
                    'nombre': curso.nombre,
                    'paralelo': curso.Paralelo,
                    'turno': curso.Turno,
                    'nivel': curso.Nivel
                },
                'docente_info': {
                    'ci': docente.ci,
                    'nombreCompleto': docente.nombreCompleto
                },
                'gestiones': [
                    {
                        'id': g.id,
                        'periodo': g.periodo,
                        'anio': g.anio
                    } for g in gestiones
                ],
                'year_filtrado': year
            }

            return {
                'estudiantes': boletin_resultado,
                'resumen': resumen,
                'mensaje': f'Boletín generado exitosamente para {total_estudiantes} estudiantes en {total_gestiones} períodos'
            }, 200

        except Exception as e:
            ns.abort(500, f'Error interno del servidor: {str(e)}')


@ns.route('/boletin-completo-estudiantes-filtrados')
class BoletinCompletoEstudiantesFiltrados(Resource):
    @jwt_required()
    @ns.doc(params={
        'docente_ci': 'CI del docente',
        'materia_id': 'ID de la materia',
        'curso_id': 'ID del curso',
        'year': 'Año de inscripción (opcional, por defecto 2025)'
    })
    def get(self):
        """Genera boletín completo de estudiantes filtrados con notas finales y estimadas por períodos para una materia específica"""
        try:
            docente_ci = request.args.get('docente_ci', type=int)
            materia_id = request.args.get('materia_id', type=int)
            curso_id = request.args.get('curso_id', type=int)
            year = request.args.get('year', type=int, default=2025)

            # Validar parámetros requeridos
            if not all([docente_ci, materia_id, curso_id]):
                ns.abort(400, 'Faltan parámetros requeridos: docente_ci, materia_id, curso_id')

            # Validar que el docente existe
            docente = Docente.query.filter_by(ci=docente_ci).first()
            if not docente:
                ns.abort(404, 'Docente no encontrado')

            # Validar que la materia existe
            materia = Materia.query.get(materia_id)
            if not materia:
                ns.abort(404, 'Materia no encontrada')

            # Validar que el curso existe
            curso = Curso.query.get(curso_id)
            if not curso:
                ns.abort(404, 'Curso no encontrado')

            # Validar que el docente enseña esa materia
            dm = DocenteMateria.query.filter_by(
                docente_ci=docente_ci,
                materia_id=materia_id
            ).first()

            if not dm:
                ns.abort(404, 'El docente no enseña esa materia')

            # Verificar que la materia pertenece a ese curso
            mc = MateriaCurso.query.filter_by(
                materia_id=materia_id,
                curso_id=curso_id
            ).first()

            if not mc:
                ns.abort(404, 'La materia no pertenece a ese curso')

            # Buscar inscripciones al curso del año especificado
            inscripciones = Inscripcion.query.filter(
                Inscripcion.curso_id == curso_id,
                func.extract('year', Inscripcion.fecha) == year
            ).all()

            # Extraer estudiantes únicos de las inscripciones
            estudiantes = list({ins.estudiante.ci: ins.estudiante for ins in inscripciones}.values())

            if not estudiantes:
                return {
                    'mensaje': 'No se encontraron estudiantes para los criterios especificados',
                    'filtros_aplicados': {
                        'docente_ci': docente_ci,
                        'materia_id': materia_id,
                        'curso_id': curso_id,
                        'year': year
                    },
                    'estudiantes': [],
                    'resumen': {}
                }, 200

            # Obtener todas las gestiones del año especificado
            gestiones = Gestion.query.filter_by(anio=year).all()
            
            if not gestiones:
                return {
                    'mensaje': f'No se encontraron gestiones para el año {year}',
                    'estudiantes': estudiantes_schema.dump(estudiantes),
                    'resumen': {}
                }, 200

            # Construir el boletín completo para cada estudiante
            boletin_resultado = []
            
            for estudiante in estudiantes:
                estudiante_boletin = {
                    'ci': estudiante.ci,
                    'nombreCompleto': estudiante.nombreCompleto,
                    'materia': {
                        'id': materia.id,
                        'nombre': materia.nombre,
                        'descripcion': materia.descripcion
                    },
                    'periodos': [],
                    'promedios': {
                        'nota_final': 0.0,
                        'nota_estimada': 0.0
                    },
                    'total_periodos': {
                        'con_nota_final': 0,
                        'con_nota_estimada': 0
                    }
                }
                
                notas_finales_por_periodo = []
                notas_estimadas_por_periodo = []
                
                # Para cada gestión (período), obtener tanto la nota final como la estimada
                for gestion in gestiones:
                    # Buscar nota final
                    nota_final = NotaFinal.query.filter_by(
                        estudiante_ci=estudiante.ci,
                        materia_id=materia_id,
                        gestion_id=gestion.id
                    ).first()
                    
                    # Buscar nota estimada
                    nota_estimada = NotaEstimada.query.filter_by(
                        estudiante_ci=estudiante.ci,
                        materia_id=materia_id,
                        gestion_id=gestion.id
                    ).first()
                    
                    periodo_info = {
                        'gestion_id': gestion.id,
                        'periodo': gestion.periodo,
                        'anio': gestion.anio,
                        'nota_final': {
                            'valor': nota_final.valor if nota_final else 0.0,
                            'tiene_nota': nota_final is not None
                        },
                        'nota_estimada': {
                            'valor': nota_estimada.valor_estimado if nota_estimada else 0.0,
                            'razon_estimacion': nota_estimada.razon_estimacion if nota_estimada else None,
                            'tiene_nota': nota_estimada is not None
                        }
                    }
                    
                    estudiante_boletin['periodos'].append(periodo_info)
                    
                    # Acumular notas para calcular promedios
                    if nota_final:
                        notas_finales_por_periodo.append(nota_final.valor)
                    
                    if nota_estimada:
                        notas_estimadas_por_periodo.append(nota_estimada.valor_estimado)
                
                # Calcular promedios
                if notas_finales_por_periodo:
                    estudiante_boletin['promedios']['nota_final'] = round(
                        sum(notas_finales_por_periodo) / len(notas_finales_por_periodo), 2
                    )
                    estudiante_boletin['total_periodos']['con_nota_final'] = len(notas_finales_por_periodo)
                
                if notas_estimadas_por_periodo:
                    estudiante_boletin['promedios']['nota_estimada'] = round(
                        sum(notas_estimadas_por_periodo) / len(notas_estimadas_por_periodo), 2
                    )
                    estudiante_boletin['total_periodos']['con_nota_estimada'] = len(notas_estimadas_por_periodo)
                
                boletin_resultado.append(estudiante_boletin)
            
            # Calcular resumen general
            total_estudiantes = len(estudiantes)
            total_gestiones = len(gestiones)
            
            # Estadísticas de cobertura de notas
            estudiantes_con_notas_finales = sum(1 for est in boletin_resultado if est['total_periodos']['con_nota_final'] > 0)
            estudiantes_con_notas_estimadas = sum(1 for est in boletin_resultado if est['total_periodos']['con_nota_estimada'] > 0)
            
            # Promedios generales de la clase
            todas_notas_finales = []
            todas_notas_estimadas = []
            
            for est in boletin_resultado:
                for periodo in est['periodos']:
                    if periodo['nota_final']['tiene_nota']:
                        todas_notas_finales.append(periodo['nota_final']['valor'])
                    if periodo['nota_estimada']['tiene_nota']:
                        todas_notas_estimadas.append(periodo['nota_estimada']['valor'])
            
            promedio_general_final = round(sum(todas_notas_finales) / len(todas_notas_finales), 2) if todas_notas_finales else 0.0
            promedio_general_estimado = round(sum(todas_notas_estimadas) / len(todas_notas_estimadas), 2) if todas_notas_estimadas else 0.0
            
            resumen = {
                'total_estudiantes': total_estudiantes,
                'total_periodos_disponibles': total_gestiones,
                'estadisticas_cobertura': {
                    'estudiantes_con_notas_finales': estudiantes_con_notas_finales,
                    'estudiantes_con_notas_estimadas': estudiantes_con_notas_estimadas,
                    'porcentaje_cobertura_final': round((estudiantes_con_notas_finales / total_estudiantes) * 100, 1) if total_estudiantes > 0 else 0,
                    'porcentaje_cobertura_estimada': round((estudiantes_con_notas_estimadas / total_estudiantes) * 100, 1) if total_estudiantes > 0 else 0
                },
                'promedios_generales': {
                    'nota_final': promedio_general_final,
                    'nota_estimada': promedio_general_estimado,
                    'total_notas_finales_registradas': len(todas_notas_finales),
                    'total_notas_estimadas_registradas': len(todas_notas_estimadas)
                },
                'materia_info': {
                    'id': materia.id,
                    'nombre': materia.nombre,
                    'descripcion': materia.descripcion
                },
                'curso_info': {
                    'id': curso.id,
                    'nombre': curso.nombre,
                    'paralelo': curso.Paralelo,
                    'turno': curso.Turno,
                    'nivel': curso.Nivel
                },
                'docente_info': {
                    'ci': docente.ci,
                    'nombreCompleto': docente.nombreCompleto
                },
                'gestiones': [
                    {
                        'id': g.id,
                        'periodo': g.periodo,
                        'anio': g.anio
                    } for g in gestiones
                ],
                'year_filtrado': year
            }

            return {
                'estudiantes': boletin_resultado,
                'resumen': resumen,
                'mensaje': f'Boletín completo generado exitosamente para {total_estudiantes} estudiantes en {total_gestiones} períodos (Notas finales y estimadas)'
            }, 200

        except Exception as e:
            ns.abort(500, f'Error interno del servidor: {str(e)}')


@ns.route('/<int:ci>/boletin-completo')
@ns.param('ci', 'CI del estudiante')
class BoletinCompletoEstudiante(Resource):
    @jwt_required()
    @ns.doc(params={
        'year': 'Año de las gestiones (opcional, por defecto 2025)'
    })
    def get(self, ci):
        """Obtiene el boletín completo de un estudiante con todas sus materias, notas finales y estimadas por período para un año específico"""
        try:
            # Obtener el año del parámetro de consulta
            year = request.args.get('year', type=int, default=2025)
            
            # Verificar que el estudiante existe
            estudiante = Estudiante.query.get(ci)
            if not estudiante:
                ns.abort(404, 'Estudiante no encontrado')

            # Obtener todas las inscripciones del estudiante para conocer sus cursos
            inscripciones = Inscripcion.query.filter_by(estudiante_ci=ci).all()
            if not inscripciones:
                return {
                    'mensaje': 'El estudiante no tiene inscripciones registradas',
                    'estudiante': {
                        'ci': estudiante.ci,
                        'nombreCompleto': estudiante.nombreCompleto
                    },
                    'materias': []
                }, 200

            # Obtener todas las materias de todos los cursos en los que está inscrito
            materias_set = set()
            cursos_info = []
            
            for inscripcion in inscripciones:
                curso = inscripcion.curso
                if curso:
                    cursos_info.append({
                        'curso_id': curso.id,
                        'nombre': curso.nombre,
                        'paralelo': curso.Paralelo,
                        'turno': curso.Turno,
                        'nivel': curso.Nivel,
                        'fecha_inscripcion': inscripcion.fecha.strftime('%Y-%m-%d') if inscripcion.fecha else None
                    })
                    
                    # Obtener materias del curso
                    materias_curso = MateriaCurso.query.filter_by(curso_id=curso.id).all()
                    for mc in materias_curso:
                        if mc.materia:
                            materias_set.add(mc.materia.id)

            # Convertir set a lista de objetos materia
            materias = [Materia.query.get(mid) for mid in materias_set if Materia.query.get(mid)]
            
            if not materias:                return {
                    'mensaje': 'No se encontraron materias para el estudiante',
                    'estudiante': {
                        'ci': estudiante.ci,
                        'nombreCompleto': estudiante.nombreCompleto
                    },
                    'cursos': cursos_info,
                    'materias': [],
                    'year_solicitado': year
                }, 200# Obtener solo las gestiones del año especificado
            gestiones = Gestion.query.filter_by(anio=year).all()
            gestiones_dict = {g.id: g for g in gestiones}
            
            if not gestiones:
                return {
                    'mensaje': f'No se encontraron gestiones para el año {year}',
                    'estudiante': {
                        'ci': estudiante.ci,
                        'nombreCompleto': estudiante.nombreCompleto
                    },
                    'cursos': cursos_info,
                    'materias': [],
                    'year_solicitado': year
                }, 200

            # Construir el boletín por materia
            boletin_materias = []
            
            for materia in materias:
                materia_boletin = {
                    'materia_id': materia.id,
                    'materia_nombre': materia.nombre,
                    'materia_descripcion': materia.descripcion,
                    'periodos': [],
                    'promedios': {
                        'nota_final': 0.0,
                        'nota_estimada': 0.0
                    },
                    'totales': {
                        'periodos_con_nota_final': 0,
                        'periodos_con_nota_estimada': 0
                    }
                }
                
                notas_finales_acumuladas = []
                notas_estimadas_acumuladas = []
                  # Para cada gestión del año especificado, buscar notas finales y estimadas
                for gestion in gestiones:
                    # Buscar nota final
                    nota_final = NotaFinal.query.filter_by(
                        estudiante_ci=ci,
                        materia_id=materia.id,
                        gestion_id=gestion.id
                    ).first()
                    
                    # Buscar nota estimada
                    nota_estimada = NotaEstimada.query.filter_by(
                        estudiante_ci=ci,
                        materia_id=materia.id,
                        gestion_id=gestion.id
                    ).first()
                    
                    # Solo agregar el período si tiene al menos una nota
                    if nota_final or nota_estimada:
                        periodo_info = {
                            'gestion_id': gestion.id,
                            'periodo': gestion.periodo,
                            'anio': gestion.anio,
                            'nota_final': {
                                'valor': nota_final.valor if nota_final else None,
                                'tiene_nota': nota_final is not None
                            },
                            'nota_estimada': {
                                'valor': nota_estimada.valor_estimado if nota_estimada else None,
                                'razon_estimacion': nota_estimada.razon_estimacion if nota_estimada else None,
                                'tiene_nota': nota_estimada is not None
                            }
                        }
                        
                        materia_boletin['periodos'].append(periodo_info)
                        
                        # Acumular notas para promedios
                        if nota_final:
                            notas_finales_acumuladas.append(nota_final.valor)
                        if nota_estimada:
                            notas_estimadas_acumuladas.append(nota_estimada.valor_estimado)
                
                # Calcular promedios
                if notas_finales_acumuladas:
                    materia_boletin['promedios']['nota_final'] = round(
                        sum(notas_finales_acumuladas) / len(notas_finales_acumuladas), 2
                    )
                    materia_boletin['totales']['periodos_con_nota_final'] = len(notas_finales_acumuladas)
                
                if notas_estimadas_acumuladas:
                    materia_boletin['promedios']['nota_estimada'] = round(
                        sum(notas_estimadas_acumuladas) / len(notas_estimadas_acumuladas), 2
                    )
                    materia_boletin['totales']['periodos_con_nota_estimada'] = len(notas_estimadas_acumuladas)
                
                # Solo agregar la materia al boletín si tiene al menos un período con notas
                if materia_boletin['periodos']:
                    boletin_materias.append(materia_boletin)

            # Calcular estadísticas generales del estudiante
            total_materias = len(boletin_materias)
            materias_con_nota_final = sum(1 for m in boletin_materias if m['totales']['periodos_con_nota_final'] > 0)
            materias_con_nota_estimada = sum(1 for m in boletin_materias if m['totales']['periodos_con_nota_estimada'] > 0)
              # Promedio general del estudiante
            todas_notas_finales = []
            todas_notas_estimadas = []
            
            for materia in boletin_materias:
                if materia['promedios']['nota_final'] > 0:
                    todas_notas_finales.append(materia['promedios']['nota_final'])
                if materia['promedios']['nota_estimada'] > 0:
                    todas_notas_estimadas.append(materia['promedios']['nota_estimada'])
            
            promedio_general_final = round(sum(todas_notas_finales) / len(todas_notas_finales), 2) if todas_notas_finales else 0.0
            promedio_general_estimado = round(sum(todas_notas_estimadas) / len(todas_notas_estimadas), 2) if todas_notas_estimadas else 0.0

            # Información de gestiones del año especificado
            gestiones_info = [
                {
                    'id': g.id,
                    'periodo': g.periodo,
                    'anio': g.anio
                } for g in gestiones
            ]

            return {
                'estudiante': {
                    'ci': estudiante.ci,
                    'nombreCompleto': estudiante.nombreCompleto,
                    'fechaNacimiento': estudiante.fechaNacimiento.strftime('%Y-%m-%d') if estudiante.fechaNacimiento else None,
                    'apoderado': estudiante.apoderado,
                    'telefono': estudiante.telefono,
                    'imagen_url': estudiante.imagen_url
                },
                'cursos': cursos_info,
                'materias': boletin_materias,
                'resumen_general': {
                    'total_materias': total_materias,
                    'materias_con_nota_final': materias_con_nota_final,
                    'materias_con_nota_estimada': materias_con_nota_estimada,
                    'promedio_general_final': promedio_general_final,
                    'promedio_general_estimado': promedio_general_estimado,
                    'total_periodos_evaluados': len(gestiones_info),
                    'year_evaluado': year
                },
                'gestiones_disponibles': gestiones_info,
                'mensaje': f'Boletín completo generado para {total_materias} materias del año {year}'
            }, 200

        except Exception as e:
            ns.abort(500, f'Error interno del servidor: {str(e)}')



