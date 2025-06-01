from ..models.Docente_Model import Docente
from ..models.DocenteMateria_Model import DocenteMateria
from ..models.MateriaCurso_Model import MateriaCurso
from ..models.Materia_Model import Materia
from ..models.Curso_Model import Curso
from ..models.Estudiante_Model import Estudiante
from ..models.Evaluacion_Model import Evaluacion
from ..models.Gestion_Model import Gestion
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


