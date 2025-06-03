from ..models.Docente_Model import Docente
from ..models.DocenteMateria_Model import DocenteMateria
from ..models.MateriaCurso_Model import MateriaCurso
from ..models.Materia_Model import Materia
from ..models.Curso_Model import Curso
from ..models.Estudiante_Model import Estudiante
from ..models.Evaluacion_Model import Evaluacion
from ..models.Gestion_Model import Gestion
from ..models.NotaFinal_Model import NotaFinal
from ..models.Inscripcion_Model import Inscripcion
from ..schemas.Docente_schema import  DocenteSchema
from ..schemas.Materia_schema import MateriaSchema
from flask import request 
from app import db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
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


# ========== FUNCIÓN AUXILIAR PARA VERIFICACIÓN DE ADMINISTRADOR ==========

def verificar_admin():
    """
    Verifica si el usuario actual es administrador (esDocente=False).
    Lanza abort(403) si no es administrador.
    """
    # Obtener la identidad del JWT (gmail del usuario)
    current_user_gmail = get_jwt_identity()
    
    # Buscar el usuario en la base de datos
    usuario = Docente.query.filter_by(gmail=current_user_gmail).first()
    
    if not usuario:
        ns.abort(401, 'Usuario no encontrado')
    
    # Verificar si es administrador (esDocente=False)
    if usuario.esDocente:
        ns.abort(403, 'Acceso denegado: Solo administradores pueden acceder a este endpoint')
    
    return usuario  # Retornar el usuario para uso posterior si es necesario

# ========== ENDPOINTS PARA DASHBOARD DEL ADMINISTRADOR ==========

@ns.route('/dashboard/admin/conteos-globales')
class ConteoGlobalPorRol(Resource):
    @jwt_required()
    def get(self):
        """Conteo global por rol - Total de docentes/estudiantes"""
        # Verificar que el usuario sea administrador
        verificar_admin()
        
        try:
            # Contar total de docentes
            total_docentes = Docente.query.count()
            
            # Contar total de estudiantes
            total_estudiantes = Estudiante.query.count()
            
            return {
                'total_docentes': total_docentes,
                'total_estudiantes': total_estudiantes,
                'total_usuarios': total_docentes + total_estudiantes,
                'mensaje': 'Conteos globales obtenidos exitosamente'
            }, 200
            
        except Exception as e:
            ns.abort(500, f'Error interno del servidor: {str(e)}')


@ns.route('/dashboard/admin/asistencia-global')
class AsistenciaGlobal(Resource):
    @jwt_required()
    @ns.doc(params={
        'gestion_id': 'ID de la gestión (opcional, última gestión por defecto)'
    })
    def get(self):
        """Asistencia de todos los estudiantes por gestión - Porcentaje de asistencia general"""
        # Verificar que el usuario sea administrador
        verificar_admin()
        
        try:
            gestion_id = request.args.get('gestion_id', type=int)
            
            # Si no se proporciona gestión, usar la más reciente
            if not gestion_id:
                gestion = Gestion.query.order_by(Gestion.anio.desc(), Gestion.id.desc()).first()
                if not gestion:
                    return {
                        'mensaje': 'No se encontraron gestiones registradas',
                        'porcentaje_asistencia': 0,
                        'estadisticas': {}
                    }, 200
                gestion_id = gestion.id
            else:
                gestion = Gestion.query.get(gestion_id)
                if not gestion:
                    ns.abort(404, 'Gestión no encontrada')
              # Obtener todas las evaluaciones de asistencia final para la gestión
            # Usando tipo_evaluacion_id = 2 para "Asistencia-Final" que contiene las notas finales
            evaluaciones_asistencia_final = Evaluacion.query.filter_by(
                gestion_id=gestion_id,
                tipo_evaluacion_id=2  # ID para Asistencia-Final
            ).all()
            
            if not evaluaciones_asistencia_final:
                return {
                    'mensaje': f'No se encontraron registros de asistencia final para la gestión {gestion.anio} - {gestion.periodo}',
                    'gestion': {
                        'id': gestion.id,
                        'anio': gestion.anio,
                        'periodo': gestion.periodo
                    },
                    'porcentaje_asistencia': 0,
                    'estadisticas': {
                        'total_evaluaciones': 0,
                        'total_estudiantes': 0,
                        'promedio_general': 0
                    }
                }, 200
            
            # Calcular estadísticas de asistencia usando regla de tres
            total_evaluaciones = len(evaluaciones_asistencia_final)
            suma_notas_actual = sum(eval.nota for eval in evaluaciones_asistencia_final)
            
            # Obtener estudiantes únicos
            estudiantes_unicos = set(eval.estudiante_ci for eval in evaluaciones_asistencia_final)
            total_estudiantes = len(estudiantes_unicos)
            
            # Calcular la asistencia máxima teórica (asumiendo nota máxima de 15 por estudiante)
            # Regla de tres: Si cada estudiante puede tener máximo 15 de asistencia
            asistencia_maxima_teorica = total_estudiantes * 15
            
            # Calcular porcentaje usando regla de tres
            # Si asistencia_maxima_teorica = 100%, entonces suma_notas_actual = X%
            porcentaje_asistencia = round((suma_notas_actual / asistencia_maxima_teorica) * 100, 2) if asistencia_maxima_teorica > 0 else 0
            
            # Calcular promedio general de notas
            promedio_general = suma_notas_actual / total_evaluaciones if total_evaluaciones > 0 else 0
            
            # Calcular promedio por estudiante para categorización
            promedios_por_estudiante = {}
            for eval in evaluaciones_asistencia_final:
                if eval.estudiante_ci not in promedios_por_estudiante:
                    promedios_por_estudiante[eval.estudiante_ci] = []
                promedios_por_estudiante[eval.estudiante_ci].append(eval.nota)            
            # Categorizar estudiantes por nivel de asistencia (escala de 15)
            estudiantes_excelente = 0  # >= 13.5 (90% de 15)
            estudiantes_buena = 0      # 10.5-13.4 (70-89% de 15)
            estudiantes_regular = 0    # 7.5-10.4 (50-69% de 15)
            estudiantes_deficiente = 0 # < 7.5 (< 50% de 15)
            
            for ci, notas in promedios_por_estudiante.items():
                promedio_estudiante = sum(notas) / len(notas)
                if promedio_estudiante >= 13.5:  # 90% de 15
                    estudiantes_excelente += 1
                elif promedio_estudiante >= 10.5:  # 70% de 15
                    estudiantes_buena += 1
                elif promedio_estudiante >= 7.5:   # 50% de 15
                    estudiantes_regular += 1
                else:
                    estudiantes_deficiente += 1
            
            return {
                'gestion': {
                    'id': gestion.id,
                    'anio': gestion.anio,
                    'periodo': gestion.periodo
                },
                'porcentaje_asistencia_general': porcentaje_asistencia,
                'calculo_regla_tres': {
                    'suma_notas_actual': round(suma_notas_actual, 2),
                    'asistencia_maxima_teorica': asistencia_maxima_teorica,
                    'formula': f'({suma_notas_actual} / {asistencia_maxima_teorica}) * 100 = {porcentaje_asistencia}%'
                },
                'estadisticas': {
                    'total_evaluaciones_asistencia_final': total_evaluaciones,
                    'total_estudiantes_evaluados': total_estudiantes,
                    'promedio_general_notas': round(promedio_general, 2),
                    'nota_maxima_por_estudiante': 15,
                    'distribucion_asistencia': {
                        'excelente_90_100': estudiantes_excelente,
                        'buena_70_89': estudiantes_buena,
                        'regular_50_69': estudiantes_regular,
                        'deficiente_0_49': estudiantes_deficiente
                    }
                },
                'mensaje': f'Estadísticas de asistencia final calculadas para {total_estudiantes} estudiantes usando regla de tres'
            }, 200
            
        except Exception as e:
            ns.abort(500, f'Error interno del servidor: {str(e)}')


@ns.route('/dashboard/admin/evaluaciones-contadas')
class EvaluacionesContadas(Resource):
    @jwt_required()
    @ns.doc(params={
        'gestion_id': 'ID de la gestión (opcional)',
        'anio': 'Año específico (opcional, ej: 2025)',
        'periodo': 'Período específico (opcional, ej: "1 trimestre")'
    })
    def get(self):
        """Conteo de evaluaciones realizadas por gestión/año/período"""
        # Verificar que el usuario sea administrador
        verificar_admin()
        
        try:
            gestion_id = request.args.get('gestion_id', type=int)
            anio = request.args.get('anio', type=int)
            periodo = request.args.get('periodo', type=str)
            
            # Construir consulta base
            query = Evaluacion.query
            
            # Si se proporciona gestion_id específico, usarlo directamente
            if gestion_id:
                gestion = Gestion.query.get(gestion_id)
                if not gestion:
                    ns.abort(404, 'Gestión no encontrada')
                query = query.filter_by(gestion_id=gestion_id)
            
            # Si se proporcionan año y/o período, filtrar por gestiones que coincidan
            elif anio or periodo:
                gestion_query = Gestion.query
                
                # Filtrar por año si se proporciona
                if anio:
                    gestion_query = gestion_query.filter_by(anio=anio)
                
                # Filtrar por período si se proporciona
                if periodo:
                    gestion_query = gestion_query.filter(
                        Gestion.periodo.ilike(f"%{periodo}%")
                    )
                
                gestiones_filtradas = gestion_query.all()
                
                if not gestiones_filtradas:
                    filtros_mensaje = []
                    if anio:
                        filtros_mensaje.append(f"año: {anio}")
                    if periodo:
                        filtros_mensaje.append(f"período: {periodo}")
                    
                    return {
                        'mensaje': f'No se encontraron gestiones para los filtros: {", ".join(filtros_mensaje)}',
                        'filtros_aplicados': {
                            'gestion_id': gestion_id,
                            'anio': anio,
                            'periodo': periodo
                        },
                        'conteos': {},
                        'total_evaluaciones': 0
                    }, 200
                
                # Filtrar evaluaciones por las gestiones encontradas
                gestion_ids = [g.id for g in gestiones_filtradas]
                query = query.filter(Evaluacion.gestion_id.in_(gestion_ids))
            
            # Obtener todas las evaluaciones filtradas
            evaluaciones = query.all()
            
            if not evaluaciones:
                return {
                    'mensaje': 'No se encontraron evaluaciones para los criterios especificados',
                    'filtros_aplicados': {
                        'gestion_id': gestion_id,
                        'periodo': periodo
                    },
                    'conteos': {},
                    'total_evaluaciones': 0
                }, 200
            
            # Agrupar conteos por gestión
            conteos_por_gestion = {}
            total_evaluaciones = len(evaluaciones)
            
            for evaluacion in evaluaciones:
                gestion = Gestion.query.get(evaluacion.gestion_id)
                if gestion:
                    gestion_key = f"{gestion.anio}_{gestion.periodo}"
                    
                    if gestion_key not in conteos_por_gestion:
                        conteos_por_gestion[gestion_key] = {
                            'gestion_info': {
                                'id': gestion.id,
                                'anio': gestion.anio,
                                'periodo': gestion.periodo
                            },
                            'total_evaluaciones': 0,
                            'evaluaciones_por_tipo': {},
                            'estudiantes_evaluados': set(),
                            'materias_evaluadas': set()
                        }
                    
                    conteos_por_gestion[gestion_key]['total_evaluaciones'] += 1
                    conteos_por_gestion[gestion_key]['estudiantes_evaluados'].add(evaluacion.estudiante_ci)
                    conteos_por_gestion[gestion_key]['materias_evaluadas'].add(evaluacion.materia_id)
                    
                    # Contar por tipo de evaluación
                    tipo_eval_id = evaluacion.tipo_evaluacion_id
                    if tipo_eval_id not in conteos_por_gestion[gestion_key]['evaluaciones_por_tipo']:
                        conteos_por_gestion[gestion_key]['evaluaciones_por_tipo'][tipo_eval_id] = 0
                    conteos_por_gestion[gestion_key]['evaluaciones_por_tipo'][tipo_eval_id] += 1
            
            # Convertir sets a conteos
            for gestion_key in conteos_por_gestion:
                conteos_por_gestion[gestion_key]['total_estudiantes_evaluados'] = len(
                    conteos_por_gestion[gestion_key]['estudiantes_evaluados']
                )
                conteos_por_gestion[gestion_key]['total_materias_evaluadas'] = len(
                    conteos_por_gestion[gestion_key]['materias_evaluadas']
                )
                # Remover los sets para la serialización JSON
                del conteos_por_gestion[gestion_key]['estudiantes_evaluados']
                del conteos_por_gestion[gestion_key]['materias_evaluadas']
            
            # Calcular estadísticas generales
            total_estudiantes_unicos = len(set(eval.estudiante_ci for eval in evaluaciones))
            total_materias_unicas = len(set(eval.materia_id for eval in evaluaciones))
            
            # Información de gestiones incluidas
            gestiones_incluidas = []
            if gestion_id:
                gestion = Gestion.query.get(gestion_id)
                gestiones_incluidas = [{'id': gestion.id, 'anio': gestion.anio, 'periodo': gestion.periodo}]
            elif periodo:
                gestiones_incluidas = [
                    {'id': g.id, 'anio': g.anio, 'periodo': g.periodo}
                    for g in Gestion.query.filter(Gestion.periodo.ilike(f"%{periodo}%")).all()
                ]
            else:
                # Todas las gestiones que tienen evaluaciones
                gestiones_con_eval = set(eval.gestion_id for eval in evaluaciones)
                gestiones_incluidas = [
                    {'id': g.id, 'anio': g.anio, 'periodo': g.periodo}
                    for g in Gestion.query.filter(Gestion.id.in_(gestiones_con_eval)).all()
                ]
            
            return {
                'filtros_aplicados': {
                    'gestion_id': gestion_id,
                    'periodo': periodo
                },
                'gestiones_incluidas': gestiones_incluidas,
                'conteos_por_gestion': conteos_por_gestion,
                'resumen_general': {
                    'total_evaluaciones': total_evaluaciones,
                    'total_estudiantes_evaluados': total_estudiantes_unicos,
                    'total_materias_evaluadas': total_materias_unicas,
                    'total_gestiones_con_evaluaciones': len(conteos_por_gestion)
                },
                'mensaje': f'Conteo de evaluaciones realizado: {total_evaluaciones} evaluaciones encontradas'
            }, 200
            
        except Exception as e:
            ns.abort(500, f'Error interno del servidor: {str(e)}')


# ========== ENDPOINTS PARA DASHBOARD DEL DOCENTE ==========

@ns.route('/dashboard/docente/<int:ci>/estudiantes-por-curso')
@ns.param('ci', 'CI del docente')
class EstudiantesPorCurso(Resource):
    @jwt_required()
    @ns.doc(params={
        'year': 'Año de inscripción (opcional, año actual por defecto)'
    })
    def get(self, ci):
        """Total de estudiantes por curso asignado al docente filtrado por año de inscripción"""
        try:
            # Verificar que el docente existe
            docente = Docente.query.get_or_404(ci)

            # Obtener parámetro de año (defaultea al año actual)
            from datetime import datetime
            year = request.args.get('year', default=datetime.now().year, type=int)

            # Obtener las materias asignadas al docente
            docente_materias = DocenteMateria.query.filter_by(docente_ci=ci).all()

            if not docente_materias:
                return {
                    'mensaje': 'El docente no tiene materias asignadas',
                    'docente': {
                        'ci': docente.ci,
                        'nombre_completo': docente.nombreCompleto
                    },
                    'year_filtrado': year,
                    'cursos': [],
                    'total_estudiantes': 0
                }, 200

            # Obtener cursos y contar estudiantes filtrado por año de inscripción
            cursos_estudiantes = {}
            total_estudiantes_general = 0

            for dm in docente_materias:
                # Obtener materias-cursos donde esté asignada esta materia
                materias_curso = MateriaCurso.query.filter_by(materia_id=dm.materia_id).all()

                for mc in materias_curso:
                    curso = mc.curso
                    if not curso:
                        continue

                    # Contar estudiantes inscritos en este curso FILTRADO POR AÑO
                    from ..models.Inscripcion_Model import Inscripcion
                    total_estudiantes_curso = Inscripcion.query.filter(
                        Inscripcion.curso_id == curso.id,
                        db.extract('year', Inscripcion.fecha) == year
                    ).count()

                    curso_key = f"{curso.id}_{curso.nombre}"
                    
                    if curso_key not in cursos_estudiantes:
                        cursos_estudiantes[curso_key] = {
                            'curso_info': {
                                'id': curso.id,
                                'nombre': curso.nombre,
                                'paralelo': curso.Paralelo,
                                'nivel': curso.Nivel
                            },
                            'total_estudiantes': total_estudiantes_curso,
                            'materias_docente': []
                        }

                    # Agregar materia a la lista si no está ya
                    materia_info = {
                        'id': dm.materia.id,
                        'nombre': dm.materia.nombre
                    }

                    if materia_info not in cursos_estudiantes[curso_key]['materias_docente']:
                        cursos_estudiantes[curso_key]['materias_docente'].append(materia_info)

            # Calcular total general (sin duplicados) filtrado por año
            cursos_unicos = set()
            for data in cursos_estudiantes.values():
                cursos_unicos.add(data['curso_info']['id'])

            total_estudiantes_general = sum(
                Inscripcion.query.filter(
                    Inscripcion.curso_id == curso_id,
                    db.extract('year', Inscripcion.fecha) == year
                ).count()
                for curso_id in cursos_unicos
            )

            return {
                'docente': {
                    'ci': docente.ci,
                    'nombre_completo': docente.nombreCompleto
                },
                'year_filtrado': year,
                'cursos': list(cursos_estudiantes.values()),
                'resumen': {
                    'total_cursos': len(cursos_estudiantes),
                    'total_estudiantes': total_estudiantes_general,
                    'total_materias_asignadas': len(docente_materias)
                },
                'mensaje': f'Información de estudiantes por curso para el docente {docente.nombreCompleto} - Año {year}'
            }, 200
        except Exception as e:
            ns.abort(500, f'Error interno del servidor: {str(e)}')


@ns.route('/dashboard/docente/<int:ci>/asistencia-promedio')
@ns.param('ci', 'CI del docente')
class AsistenciaPromedio(Resource):
    @jwt_required()
    @ns.doc(params={
        'gestion_id': 'ID de la gestión (opcional, última gestión por defecto)'
    })
    def get(self, ci):
        """Promedio de asistencia diaria por materia/curso del docente"""
        try:
            # Verificar que el docente existe
            docente = Docente.query.get_or_404(ci)
            
            # Obtener gestión
            gestion_id = request.args.get('gestion_id', type=int)
            if not gestion_id:
                gestion = Gestion.query.order_by(Gestion.anio.desc(), Gestion.id.desc()).first()
                if not gestion:
                    return {
                        'mensaje': 'No se encontraron gestiones registradas',
                        'asistencia_promedio': {},
                        'promedio_general': 0
                    }, 200
                gestion_id = gestion.id
            else:
                gestion = Gestion.query.get(gestion_id)
                if not gestion:
                    ns.abort(404, 'Gestión no encontrada')
            
            # Obtener las materias asignadas al docente
            docente_materias = DocenteMateria.query.filter_by(docente_ci=ci).all()
            
            if not docente_materias:                return {
                    'mensaje': 'El docente no tiene materias asignadas',
                    'docente': {
                        'ci': docente.ci,
                        'nombre_completo': docente.nombreCompleto
                    },
                    'asistencia_promedio': {},
                    'promedio_general': 0
                }, 200
            
            asistencia_por_materia = {}
            suma_promedios = 0
            materias_con_datos = 0
            
            for dm in docente_materias:
                materia = dm.materia
                
                # Obtener todas las evaluaciones de asistencia final (tipo 2) para esta materia y gestión
                evaluaciones_asistencia = Evaluacion.query.filter_by(
                    materia_id=materia.id,
                    gestion_id=gestion_id,
                    tipo_evaluacion_id=2  # Asistencia-Final
                ).all()
                
                if evaluaciones_asistencia:
                    # Calcular promedio de asistencia para esta materia
                    suma_notas = sum(eval.nota for eval in evaluaciones_asistencia)
                    promedio_materia = suma_notas / len(evaluaciones_asistencia)
                    
                    # Convertir a porcentaje (escala de 15 a 100%)
                    porcentaje_asistencia = round((promedio_materia / 15) * 100, 2)
                    
                    asistencia_por_materia[f"materia_{materia.id}"] = {
                        'materia_info': {
                            'id': materia.id,
                            'nombre': materia.nombre
                        },
                        'promedio_asistencia_nota': round(promedio_materia, 2),
                        'porcentaje_asistencia': porcentaje_asistencia,
                        'total_evaluaciones': len(evaluaciones_asistencia),
                        'total_estudiantes_evaluados': len(set(eval.estudiante_ci for eval in evaluaciones_asistencia))
                    }
                    
                    suma_promedios += porcentaje_asistencia
                    materias_con_datos += 1
            
            # Calcular promedio general
            promedio_general = round(suma_promedios / materias_con_datos, 2) if materias_con_datos > 0 else 0
            return {
                'docente': {
                    'ci': docente.ci,
                    'nombre_completo': docente.nombreCompleto
                },
                'gestion': {
                    'id': gestion.id,
                    'anio': gestion.anio,
                    'periodo': gestion.periodo
                },
                'asistencia_por_materia': asistencia_por_materia,
                'resumen': {
                    'promedio_general_asistencia': promedio_general,
                    'total_materias_con_datos': materias_con_datos,
                    'total_materias_asignadas': len(docente_materias)
                },
                'mensaje': f'Promedio de asistencia calculado para {materias_con_datos} materias del docente'
            }, 200
            
        except Exception as e:
            ns.abort(500, f'Error interno del servidor: {str(e)}')


@ns.route('/dashboard/docente/<int:ci>/notas-promedio')
@ns.param('ci', 'CI del docente')
class NotasPromedio(Resource):
    @jwt_required()
    @ns.doc(params={
        'gestion_id': 'ID de la gestión (opcional, última gestión por defecto)'
    })
    def get(self, ci):
        """Promedio de notas finales por materia del docente"""
        try:
            # Verificar que el docente existe
            docente = Docente.query.get_or_404(ci)
            
            # Obtener gestión
            gestion_id = request.args.get('gestion_id', type=int)
            if not gestion_id:
                gestion = Gestion.query.order_by(Gestion.anio.desc(), Gestion.id.desc()).first()
                if not gestion:
                    return {
                        'mensaje': 'No se encontraron gestiones registradas',
                        'notas_promedio': {},
                        'promedio_general': 0
                    }, 200
                gestion_id = gestion.id
            else:
                gestion = Gestion.query.get(gestion_id)
                if not gestion:
                    ns.abort(404, 'Gestión no encontrada')
            
            # Obtener las materias asignadas al docente
            docente_materias = DocenteMateria.query.filter_by(docente_ci=ci).all()
            
            if not docente_materias:                return {
                    'mensaje': 'El docente no tiene materias asignadas',
                    'docente': {
                        'ci': docente.ci,
                        'nombre_completo': docente.nombreCompleto
                    },
                    'notas_promedio': {},
                    'promedio_general': 0
                }, 200
            
            from ..models.NotaFinal_Model import NotaFinal
            
            notas_por_materia = {}
            suma_promedios = 0
            materias_con_datos = 0
            
            for dm in docente_materias:
                materia = dm.materia
                
                # Obtener todas las notas finales para esta materia y gestión
                notas_finales = NotaFinal.query.filter_by(
                    materia_id=materia.id,
                    gestion_id=gestion_id
                ).all()
                
                if notas_finales:
                    # Calcular promedio de notas para esta materia
                    suma_notas = sum(nota.valor for nota in notas_finales)
                    promedio_materia = suma_notas / len(notas_finales)
                    
                    # Categorizar el promedio
                    if promedio_materia >= 61:
                        categoria = "Excelente"
                    elif promedio_materia >= 51:
                        categoria = "Bueno"
                    elif promedio_materia >= 36:
                        categoria = "Regular"
                    else:
                        categoria = "Deficiente"
                    
                    notas_por_materia[f"materia_{materia.id}"] = {
                        'materia_info': {
                            'id': materia.id,
                            'nombre': materia.nombre
                        },
                        'promedio_notas': round(promedio_materia, 2),
                        'categoria': categoria,
                        'total_estudiantes': len(notas_finales),
                        'distribucion_notas': {
                            'aprobados': len([n for n in notas_finales if n.valor >= 51]),
                            'reprobados': len([n for n in notas_finales if n.valor < 51]),
                            'nota_maxima': max(nota.valor for nota in notas_finales),
                            'nota_minima': min(nota.valor for nota in notas_finales)
                        }
                    }
                    
                    suma_promedios += promedio_materia
                    materias_con_datos += 1
            
            # Calcular promedio general
            promedio_general = round(suma_promedios / materias_con_datos, 2) if materias_con_datos > 0 else 0
            
            # Categorizar promedio general
            if promedio_general >= 61:
                categoria_general = "Excelente"
            elif promedio_general >= 51:
                categoria_general = "Bueno"
            elif promedio_general >= 36:
                categoria_general = "Regular"
            else:
                categoria_general = "Deficiente"
            return {
                'docente': {
                    'ci': docente.ci,
                    'nombre_completo': docente.nombreCompleto
                },
                'gestion': {
                    'id': gestion.id,
                    'anio': gestion.anio,
                    'periodo': gestion.periodo
                },
                'notas_por_materia': notas_por_materia,
                'resumen': {
                    'promedio_general': promedio_general,
                    'categoria_general': categoria_general,
                    'total_materias_con_datos': materias_con_datos,
                    'total_materias_asignadas': len(docente_materias)
                },
                'mensaje': f'Promedio de notas calculado para {materias_con_datos} materias del docente'
            }, 200
            
        except Exception as e:
            ns.abort(500, f'Error interno del servidor: {str(e)}')


@ns.route('/dashboard/docente/<string:ci>/mejores-peores-estudiantes')
class MejoresPeoresEstudiantes(Resource):
    @jwt_required()
    @ns.doc(params={
        'year': 'Año para filtrar (opcional, por defecto año actual)'
    })
    def get(self, ci):
        """Obtener top 3 mejores y peores estudiantes por materia que enseña el docente"""
        try:
            # Verificar que el docente existe
            docente = Docente.query.filter_by(ci=ci).first()
            if not docente:
                ns.abort(404, 'Docente no encontrado')
            
            # Obtener el año para filtrar
            year = request.args.get('year', type=int)
            if not year:
                year = datetime.now().year            # Obtener todas las materias asignadas al docente 
            docente_materias = DocenteMateria.query.filter_by(docente_ci=docente.ci).all()
            
            if not docente_materias:
                return {
                    'mensaje': 'El docente no tiene materias asignadas',
                    'docente': {
                        'ci': docente.ci,
                        'nombre_completo': docente.nombreCompleto
                    },
                    'year': year,
                    'materias_con_estudiantes': {}
                }, 200
            
            # Obtener gestiones del año especificado
            gestiones = Gestion.query.filter_by(anio=year).all()
            
            if not gestiones:
                return {
                    'mensaje': f'No se encontraron gestiones para el año {year}',
                    'docente': {
                        'ci': docente.ci,
                        'nombre_completo': docente.nombreCompleto
                    },
                    'year': year,
                    'materias_con_estudiantes': {}
                }, 200            
            materias_resultados = {}
            gestion_ids = [g.id for g in gestiones]
            
            for docente_materia in docente_materias:
                materia = Materia.query.get(docente_materia.materia_id)
                if not materia:
                    continue
                
                # Obtener notas finales de estudiantes para esta materia en las gestiones del año especificado
                notas_estudiantes = db.session.query(
                    NotaFinal,
                    Estudiante
                ).join(
                    Estudiante,
                    NotaFinal.estudiante_ci == Estudiante.ci
                ).filter(
                    NotaFinal.materia_id == materia.id,
                    NotaFinal.gestion_id.in_(gestion_ids)
                ).all()
                
                if not notas_estudiantes:
                    materias_resultados[f"materia_{materia.id}"] = {
                        'materia_info': {
                            'id': materia.id,
                            'nombre': materia.nombre
                        },
                        'mensaje': 'No hay notas registradas para esta materia',
                        'mejores_estudiantes': [],
                        'peores_estudiantes': [],
                        'total_estudiantes': 0
                    }
                    continue
                
                # Crear lista de estudiantes con sus notas
                estudiantes_notas = []
                for nota_final, estudiante in notas_estudiantes:
                    estudiante_data = {
                        'estudiante_id': estudiante.id,
                        'ci': estudiante.ci,
                        'nombre_completo': estudiante.nombreCompleto,
                        'nota_final': nota_final.valor,
                        'estado': 'Aprobado' if nota_final.valor >= 51 else 'Reprobado'
                    }
                    estudiantes_notas.append(estudiante_data)
                
                # Ordenar por nota (mayor a menor)
                estudiantes_ordenados = sorted(
                    estudiantes_notas, 
                    key=lambda x: x['nota_final'], 
                    reverse=True
                )
                
                # Top 3 mejores (los primeros 3)
                mejores_3 = estudiantes_ordenados[:3]
                
                # Top 3 peores (los últimos 3, pero ordenados de peor a mejor)
                peores_3 = estudiantes_ordenados[-3:]
                peores_3.reverse()  # Para mostrar del peor al menos peor
                
                # Calcular estadísticas adicionales
                notas_valores = [est['nota_final'] for est in estudiantes_notas]
                promedio_materia = sum(notas_valores) / len(notas_valores)
                nota_maxima = max(notas_valores)
                nota_minima = min(notas_valores)
                aprobados = len([n for n in notas_valores if n >= 51])
                reprobados = len(notas_valores) - aprobados
                
                materias_resultados[f"materia_{materia.id}"] = {
                    'materia_info': {
                        'id': materia.id,
                        'nombre': materia.nombre
                    },
                    'mejores_estudiantes': mejores_3,
                    'peores_estudiantes': peores_3,
                    'estadisticas': {
                        'total_estudiantes': len(estudiantes_notas),
                        'promedio_materia': round(promedio_materia, 2),
                        'nota_maxima': nota_maxima,
                        'nota_minima': nota_minima,
                        'aprobados': aprobados,
                        'reprobados': reprobados,
                        'porcentaje_aprobacion': round((aprobados / len(notas_valores)) * 100, 2)
                    }
                }
            
            return {
                'docente': {
                    'ci': docente.ci,
                    'nombre_completo': docente.nombreCompleto
                },
                'year': year,
                'materias_con_estudiantes': materias_resultados,
                'resumen': {
                    'total_materias_evaluadas': len([m for m in materias_resultados.values() if m.get('estadisticas')]),
                    'total_materias_asignadas': len(docente_materias)
                },
                'mensaje': f'Ranking de estudiantes obtenido para {len(materias_resultados)} materias del docente'
            }, 200
            
        except Exception as e:
            ns.abort(500, f'Error interno del servidor: {str(e)}')


