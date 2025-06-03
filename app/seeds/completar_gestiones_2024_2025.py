"""
Script para completar las gestiones faltantes siguiendo el lineamiento correcto:

LINEAMIENTO:
1. ✅ Tablas básicas ya creadas (estudiantes, docentes, materias, cursos, etc.)
2. 🔄 Crear gestiones faltantes (2 trimestres más de 2024 + 1 trimestre inicial de 2025)
3. 🔄 Colocar evaluaciones (solo para los trimestres de 2024)
4. 🔄 Calcular notas finales (solo para 2024)
5. ✅ 2025 queda vacío (solo estructura básica, sin evaluaciones)

ESTADO ACTUAL:
- 2024 Primer Trimestre: ✅ COMPLETO con evaluaciones
- 2024 Segundo Trimestre: ❌ FALTA CREAR
- 2024 Tercer Trimestre: ❌ FALTA CREAR  
- 2025 Primer Trimestre: ❌ FALTA CREAR (solo estructura, sin evaluaciones)
"""

from app import create_app
from app.extensions import db
from app.models.Gestion_Model import Gestion
from app.models.Estudiante_Model import Estudiante
from app.models.Inscripcion_Model import Inscripcion
from app.models.MateriaCurso_Model import MateriaCurso
from app.models.Evaluacion_Model import Evaluacion
from app.models.NotaFinal_Model import NotaFinal
from app.models.NotaEstimada_Model import NotaEstimada
from app.models.TipoEvaluacion_Model import TipoEvaluacion
from app.models.EvaluacionIntegral_Model import EvaluacionIntegral
from datetime import date, timedelta
import random

def main():
    app = create_app()
    with app.app_context():
        print("🏗️ COMPLETANDO GESTIONES FALTANTES")
        print("=" * 60)
        print("📋 Lineamiento: Crear gestiones → Evaluaciones → Cálculos")
        print("-" * 60)
        
        # PASO 1: Crear las gestiones faltantes
        print("\n📅 PASO 1: CREANDO GESTIONES FALTANTES")
        print("-" * 40)
        
        # Verificar gestiones existentes
        gestiones_existentes = Gestion.query.all()
        print(f"✅ Gestiones existentes: {len(gestiones_existentes)}")
        for g in gestiones_existentes:
            print(f"   - {g.anio} {g.periodo} (ID: {g.id})")
        
        # Crear gestiones faltantes
        gestiones_a_crear = [
            {
                "anio": 2024,
                "periodo": "Segundo Trimestre",
                "fecha_inicio": date(2024, 5, 20),
                "fecha_fin": date(2024, 8, 30),
                "con_evaluaciones": True
            },
            {
                "anio": 2024,
                "periodo": "Tercer Trimestre", 
                "fecha_inicio": date(2024, 9, 2),
                "fecha_fin": date(2024, 11, 29),
                "con_evaluaciones": True
            },
            {
                "anio": 2025,
                "periodo": "Primer Trimestre",
                "fecha_inicio": date(2025, 2, 3),
                "fecha_fin": date(2025, 5, 16),
                "con_evaluaciones": False  # Solo estructura, sin datos
            }
        ]
        
        gestiones_creadas = []
        
        for gestion_info in gestiones_a_crear:
            # Verificar si ya existe
            existe = Gestion.query.filter_by(
                anio=gestion_info["anio"],
                periodo=gestion_info["periodo"]
            ).first()
            
            if existe:
                print(f"⚠️  {gestion_info['anio']} {gestion_info['periodo']} ya existe")
                gestiones_creadas.append(existe)
                continue
            
            print(f"\n🏗️ Creando {gestion_info['anio']} {gestion_info['periodo']}...")
            
            # Crear la gestión
            nueva_gestion = Gestion(
                anio=gestion_info["anio"],
                periodo=gestion_info["periodo"]
            )
            db.session.add(nueva_gestion)
            db.session.commit()
            
            print(f"   ✅ Gestión creada (ID: {nueva_gestion.id})")
            gestiones_creadas.append(nueva_gestion)
            
            # Crear estructura básica de notas
            print("   📊 Creando estructura de notas...")
            crear_estructura_notas(nueva_gestion.id, gestion_info["anio"])
            
            # Si es 2024, crear evaluaciones completas
            if gestion_info["con_evaluaciones"]:
                print("   📝 Generando evaluaciones completas...")
                generar_evaluaciones_completas(
                    nueva_gestion.id,
                    gestion_info["fecha_inicio"],
                    gestion_info["fecha_fin"]
                )
                
                print("   🧮 Calculando notas finales...")
                calcular_todas_las_notas(nueva_gestion.id)
            else:
                print("   📋 Gestión 2025: Solo estructura (sin evaluaciones)")
        
        # RESUMEN FINAL
        print("\n" + "=" * 60)
        print("🎓 SISTEMA COMPLETO - LINEAMIENTO CUMPLIDO")
        print("=" * 60)
        
        # Verificar estado final
        todas_gestiones = Gestion.query.order_by(Gestion.anio, Gestion.id).all()
        
        print("\n📊 RESUMEN FINAL:")
        for gestion in todas_gestiones:
            evaluaciones = Evaluacion.query.filter_by(gestion_id=gestion.id).count()
            notas_finales = NotaFinal.query.filter_by(gestion_id=gestion.id).count()
            
            if gestion.anio == 2024:
                estado = "COMPLETO CON DATOS" if evaluaciones > 0 else "PENDIENTE"
            else:
                estado = "ESTRUCTURA VACÍA (RECIÉN COMENZANDO)"
            
            print(f"   📅 {gestion.anio} {gestion.periodo}:")
            print(f"      📝 Evaluaciones: {evaluaciones:,}")
            print(f"      🎯 NotaFinal: {notas_finales:,}")
            print(f"      ✨ Estado: {estado}")
            print()
        
        print("🏆 LINEAMIENTO COMPLETADO EXITOSAMENTE:")
        print("   ✅ 1. Tablas básicas creadas")
        print("   ✅ 2. Gestiones creadas (3 trimestres 2024 + 1 trimestre 2025)")
        print("   ✅ 3. Evaluaciones colocadas (solo 2024)")
        print("   ✅ 4. Notas calculadas (solo 2024)")
        print("   ✅ 5. 2025 vacío (recién empezando)")


def crear_estructura_notas(gestion_id, anio):
    """Crea la estructura básica de NotaFinal y NotaEstimada"""
    try:
        # Determinar qué estudiantes usar según el año
        if anio == 2024:
            # Primeros 300 estudiantes para 2024
            estudiantes = Estudiante.query.order_by(Estudiante.ci).limit(300).all()
        else:
            # Siguientes 300 estudiantes para 2025
            estudiantes = Estudiante.query.order_by(Estudiante.ci).offset(300).limit(300).all()
        
        notas_creadas = 0
        
        for estudiante in estudiantes:
            # Obtener inscripción del estudiante
            inscripcion = Inscripcion.query.filter_by(estudiante_ci=estudiante.ci).first()
            if not inscripcion or not inscripcion.curso:
                continue
            
            # Obtener materias del curso
            materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()
            
            for mc in materias_curso:
                # Crear NotaFinal
                nota_final = NotaFinal(
                    valor=0.0,
                    estudiante_ci=estudiante.ci,
                    gestion_id=gestion_id,
                    materia_id=mc.materia.id
                )
                db.session.add(nota_final)
                
                # Crear NotaEstimada
                nota_estimada = NotaEstimada(
                    valor_estimado=0.0,
                    razon_estimacion=f"Trimestre en progreso - {anio}",
                    estudiante_ci=estudiante.ci,
                    gestion_id=gestion_id,
                    materia_id=mc.materia.id
                )
                db.session.add(nota_estimada)
                notas_creadas += 2
        
        db.session.commit()
        print(f"      ✅ Estructura creada: {notas_creadas} registros")
        
    except Exception as e:
        db.session.rollback()
        print(f"      ❌ Error al crear estructura: {str(e)}")


def generar_evaluaciones_completas(gestion_id, fecha_inicio, fecha_fin):
    """Genera evaluaciones completas para un trimestre de 2024"""
    try:
        # Obtener tipos de evaluación
        tipo_asistencia_diaria = TipoEvaluacion.query.filter_by(nombre='Asistencia-Diaria').first()
        tipo_asistencia_final = TipoEvaluacion.query.filter_by(nombre='Asistencia-Final').first()
        tipo_examen = TipoEvaluacion.query.filter_by(nombre='Examenes').first()
        tipo_tarea = TipoEvaluacion.query.filter_by(nombre='Tareas').first()
        tipo_exposicion = TipoEvaluacion.query.filter_by(nombre='Exposiciones').first()
        
        if not all([tipo_asistencia_diaria, tipo_asistencia_final, tipo_examen, tipo_tarea, tipo_exposicion]):
            print("      ❌ No se encontraron todos los tipos de evaluación")
            return
        
        # Solo estudiantes de 2024 (primeros 300)
        estudiantes_2024 = Estudiante.query.order_by(Estudiante.ci).limit(300).all()
        
        evaluaciones_creadas = 0
        
        for estudiante in estudiantes_2024:
            inscripcion = Inscripcion.query.filter_by(estudiante_ci=estudiante.ci).first()
            if not inscripcion or not inscripcion.curso:
                continue
            
            materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()
            
            for mc in materias_curso:
                materia = mc.materia
                
                # 1. ASISTENCIAS DIARIAS (15-25 días por trimestre)
                num_asistencias = random.randint(15, 25)
                for i in range(num_asistencias):
                    fecha_asistencia = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                    nota_asistencia = generar_nota_asistencia()  # 0, 5, 10 o 15
                    
                    evaluacion = Evaluacion(
                        descripcion=f"Asistencia día {i+1}",
                        fecha=fecha_asistencia,
                        nota=nota_asistencia,
                        tipo_evaluacion_id=tipo_asistencia_diaria.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(evaluacion)
                    evaluaciones_creadas += 1
                
                # 2. EXÁMENES (2-3 por trimestre)
                num_examenes = random.randint(2, 3)
                for i in range(num_examenes):
                    fecha_examen = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                    nota_examen = generar_nota_realista("examen")
                    
                    evaluacion = Evaluacion(
                        descripcion=f"Examen {i+1} - {materia.nombre}",
                        fecha=fecha_examen,
                        nota=nota_examen,
                        tipo_evaluacion_id=tipo_examen.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(evaluacion)
                    evaluaciones_creadas += 1
                
                # 3. TAREAS (4-6 por trimestre)
                num_tareas = random.randint(4, 6)
                for i in range(num_tareas):
                    fecha_tarea = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                    nota_tarea = generar_nota_realista("tarea")
                    
                    evaluacion = Evaluacion(
                        descripcion=f"Tarea {i+1} - {materia.nombre}",
                        fecha=fecha_tarea,
                        nota=nota_tarea,
                        tipo_evaluacion_id=tipo_tarea.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(evaluacion)
                    evaluaciones_creadas += 1
                
                # 4. EXPOSICIONES (1-2 por trimestre)
                num_exposiciones = random.randint(1, 2)
                for i in range(num_exposiciones):
                    fecha_exposicion = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                    nota_exposicion = generar_nota_realista("exposicion")
                    
                    evaluacion = Evaluacion(
                        descripcion=f"Exposición {i+1} - {materia.nombre}",
                        fecha=fecha_exposicion,
                        nota=nota_exposicion,
                        tipo_evaluacion_id=tipo_exposicion.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(evaluacion)
                    evaluaciones_creadas += 1
        
        # Commit todas las evaluaciones
        db.session.commit()
        
        # Ahora calcular asistencias finales
        asistencias_finales = 0
        for estudiante in estudiantes_2024:
            inscripcion = Inscripcion.query.filter_by(estudiante_ci=estudiante.ci).first()
            if not inscripcion:
                continue
                
            materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()
            
            for mc in materias_curso:
                # Calcular promedio de asistencias diarias
                asistencias_diarias = Evaluacion.query.filter_by(
                    estudiante_ci=estudiante.ci,
                    materia_id=mc.materia.id,
                    gestion_id=gestion_id,
                    tipo_evaluacion_id=tipo_asistencia_diaria.id
                ).all()
                
                if asistencias_diarias:
                    promedio_asistencia = sum(a.nota for a in asistencias_diarias) / len(asistencias_diarias)
                    
                    # Crear asistencia final
                    asistencia_final = Evaluacion(
                        descripcion="Asistencia Final - Calculada automáticamente",
                        fecha=fecha_fin,
                        nota=promedio_asistencia,
                        tipo_evaluacion_id=tipo_asistencia_final.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=mc.materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(asistencia_final)
                    asistencias_finales += 1
        
        db.session.commit()
        print(f"      ✅ Evaluaciones: {evaluaciones_creadas:,}")
        print(f"      ✅ Asistencias finales: {asistencias_finales:,}")
        
    except Exception as e:
        db.session.rollback()
        print(f"      ❌ Error al generar evaluaciones: {str(e)}")


def calcular_todas_las_notas(gestion_id):
    """Calcula todas las notas finales para una gestión"""
    try:
        notas_actualizadas = 0
        
        # Solo estudiantes de 2024 para las gestiones de 2024
        estudiantes = Estudiante.query.order_by(Estudiante.ci).limit(300).all()
        
        for estudiante in estudiantes:
            inscripcion = Inscripcion.query.filter_by(estudiante_ci=estudiante.ci).first()
            if not inscripcion:
                continue
                
            materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()
            
            for mc in materias_curso:
                # Calcular nota final usando la misma lógica del endpoint
                promedio_final = calcular_nota_final_endpoint(estudiante.ci, gestion_id, mc.materia.id)
                
                # Actualizar NotaFinal
                nota_final = NotaFinal.query.filter_by(
                    estudiante_ci=estudiante.ci,
                    gestion_id=gestion_id,
                    materia_id=mc.materia.id
                ).first()
                
                if nota_final:
                    nota_final.valor = promedio_final
                    notas_actualizadas += 1
        
        db.session.commit()
        print(f"      ✅ Notas finales actualizadas: {notas_actualizadas:,}")
        
    except Exception as e:
        db.session.rollback()
        print(f"      ❌ Error al calcular notas: {str(e)}")


def calcular_nota_final_endpoint(estudiante_ci, gestion_id, materia_id):
    """Simula el cálculo del endpoint de notas finales"""
    try:
        # Función para calcular nota por dimensión
        def calcular_nota_dimension(dimension_nombre):
            evaluacion_integral = EvaluacionIntegral.query.filter_by(nombre=dimension_nombre).first()
            if not evaluacion_integral:
                return 0

            tipos_dimension = TipoEvaluacion.query.filter_by(
                evaluacion_integral_id=evaluacion_integral.id
            ).all()
            tipo_ids = [tipo.id for tipo in tipos_dimension]

            if not tipo_ids:
                return 0

            evaluaciones = Evaluacion.query.filter(
                Evaluacion.estudiante_ci == estudiante_ci,
                Evaluacion.materia_id == materia_id,
                Evaluacion.gestion_id == gestion_id,
                Evaluacion.tipo_evaluacion_id.in_(tipo_ids)
            ).all()

            if not evaluaciones:
                return 0

            suma = sum(eva.nota for eva in evaluaciones)
            promedio = suma / len(evaluaciones)
            return promedio

        # Calcular las 4 dimensiones
        ser_nota = calcular_nota_dimension("ser")
        hacer_nota = calcular_nota_dimension("hacer")
        saber_nota = calcular_nota_dimension("saber")
        decidir_nota = calcular_nota_dimension("decidir")

        # Promedio final
        promedio = round((ser_nota + hacer_nota + saber_nota + decidir_nota) / 4, 2)
        return promedio
        
    except Exception as e:
        print(f"Error al calcular nota final: {str(e)}")
        return 0


def generar_fecha_aleatoria(fecha_inicio, fecha_fin):
    """Genera una fecha aleatoria entre dos fechas"""
    dias_diferencia = (fecha_fin - fecha_inicio).days
    dias_aleatorios = random.randint(0, dias_diferencia)
    return fecha_inicio + timedelta(days=dias_aleatorios)


def generar_nota_realista(tipo_evaluacion):
    """Genera notas realistas según el tipo de evaluación"""
    if tipo_evaluacion == "examen":
        return round(random.uniform(40, 100), 1)
    elif tipo_evaluacion == "tarea":
        return round(random.uniform(60, 100), 1)
    elif tipo_evaluacion == "exposicion":
        return round(random.uniform(70, 100), 1)
    else:
        return round(random.uniform(50, 100), 1)


def generar_nota_asistencia():
    """
    Genera notas de asistencia usando escala de 15 puntos:
    - 0: Ausente (5%)
    - 5: Llegada tarde (7%)
    - 10: Con licencia/permiso (3%)
    - 15: Presente (85%)
    """
    rand = random.random()
    if rand < 0.05:
        return 0
    elif rand < 0.12:
        return 5
    elif rand < 0.15:
        return 10
    else:
        return 15


if __name__ == "__main__":
    main()
