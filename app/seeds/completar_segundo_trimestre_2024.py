#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPLETAR SEGUNDO TRIMESTRE 2024
Genera evaluaciones realistas para el segundo trimestre de 2024
"""

import os
import sys
import random
from datetime import date, timedelta

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models.Estudiante_Model import Estudiante
from app.models.Inscripcion_Model import Inscripcion
from app.models.Materia_Model import Materia
from app.models.MateriaCurso_Model import MateriaCurso
from app.models.Gestion_Model import Gestion
from app.models.Evaluacion_Model import Evaluacion
from app.models.TipoEvaluacion_Model import TipoEvaluacion
from app.models.NotaFinal_Model import NotaFinal
from app.extensions import db

def generar_evaluaciones_segundo_trimestre():
    """Genera evaluaciones para el segundo trimestre 2024"""
    app = create_app()
    with app.app_context():
        try:
            print("🏫 COMPLETANDO SEGUNDO TRIMESTRE 2024")
            print("=" * 50)
            
            # Verificar que existe la gestión
            gestion_2 = Gestion.query.filter_by(anio=2024, periodo="Segundo Trimestre").first()
            if not gestion_2:
                print("❌ No se encontró el Segundo Trimestre 2024")
                return False
                
            # Verificar si ya tiene evaluaciones
            evaluaciones_existentes = Evaluacion.query.filter_by(gestion_id=gestion_2.id).count()
            if evaluaciones_existentes > 0:
                print(f"⚠️ Ya existen {evaluaciones_existentes} evaluaciones. ¿Continuar? (y/n)")
                respuesta = input().lower()
                if respuesta != 'y':
                    return False
            
            # Fechas del segundo trimestre
            fecha_inicio = date(2024, 5, 20)
            fecha_fin = date(2024, 8, 30)
            
            # Obtener tipos de evaluación
            tipo_examen = TipoEvaluacion.query.filter_by(nombre='Examenes').first()
            tipo_tarea = TipoEvaluacion.query.filter_by(nombre='Tareas').first()
            tipo_exposicion = TipoEvaluacion.query.filter_by(nombre='Exposiciones').first()
            tipo_asistencia_diaria = TipoEvaluacion.query.filter_by(nombre='Asistencia-Diaria').first()
            tipo_asistencia_final = TipoEvaluacion.query.filter_by(nombre='Asistencia-Final').first()
            
            if not all([tipo_examen, tipo_tarea, tipo_exposicion, tipo_asistencia_diaria, tipo_asistencia_final]):
                print("❌ No se encontraron todos los tipos de evaluación")
                return False
            
            # Obtener estudiantes de 2024 (primeros 300)
            estudiantes_2024 = Estudiante.query.order_by(Estudiante.ci).limit(300).all()
            print(f"📚 Procesando {len(estudiantes_2024)} estudiantes...")
            
            evaluaciones_creadas = 0
            estudiantes_procesados = 0
            
            for estudiante in estudiantes_2024:
                # Obtener inscripción del estudiante
                inscripcion = Inscripcion.query.filter_by(estudiante_ci=estudiante.ci).first()
                if not inscripcion or not inscripcion.curso:
                    continue
                
                # Obtener materias del curso
                materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()
                
                for mc in materias_curso:
                    materia = mc.materia
                    
                    # Verificar si ya tiene evaluaciones en esta gestión y materia
                    eval_existente = Evaluacion.query.filter_by(
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_2.id
                    ).first()
                    
                    if eval_existente:
                        continue  # Ya tiene evaluaciones, saltar
                    
                    # 1. EXÁMENES (2-3 por trimestre)
                    num_examenes = random.randint(2, 3)
                    for i in range(num_examenes):
                        fecha_examen = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                        nota_examen = generar_nota_realista("examen")
                        
                        evaluacion = Evaluacion(
                            descripcion=f"Examen {i+1} - Segundo Trimestre",
                            fecha=fecha_examen,
                            nota=nota_examen,
                            tipo_evaluacion_id=tipo_examen.id,
                            estudiante_ci=estudiante.ci,
                            materia_id=materia.id,
                            gestion_id=gestion_2.id
                        )
                        db.session.add(evaluacion)
                        evaluaciones_creadas += 1
                    
                    # 2. TAREAS (4-6 por trimestre)
                    num_tareas = random.randint(4, 6)
                    for i in range(num_tareas):
                        fecha_tarea = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                        nota_tarea = generar_nota_realista("tarea")
                        
                        evaluacion = Evaluacion(
                            descripcion=f"Tarea {i+1} - Segundo Trimestre",
                            fecha=fecha_tarea,
                            nota=nota_tarea,
                            tipo_evaluacion_id=tipo_tarea.id,
                            estudiante_ci=estudiante.ci,
                            materia_id=materia.id,
                            gestion_id=gestion_2.id
                        )
                        db.session.add(evaluacion)
                        evaluaciones_creadas += 1
                    
                    # 3. EXPOSICIONES (1-2 por trimestre)
                    num_exposiciones = random.randint(1, 2)
                    for i in range(num_exposiciones):
                        fecha_exposicion = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                        nota_exposicion = generar_nota_realista("exposicion")
                        
                        evaluacion = Evaluacion(
                            descripcion=f"Exposición {i+1} - Segundo Trimestre",
                            fecha=fecha_exposicion,
                            nota=nota_exposicion,
                            tipo_evaluacion_id=tipo_exposicion.id,
                            estudiante_ci=estudiante.ci,
                            materia_id=materia.id,
                            gestion_id=gestion_2.id
                        )
                        db.session.add(evaluacion)
                        evaluaciones_creadas += 1
                    
                    # 4. ASISTENCIAS DIARIAS (15-25 días)
                    num_asistencias = random.randint(15, 25)
                    for i in range(num_asistencias):
                        fecha_asistencia = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                        nota_asistencia = generar_nota_asistencia()
                        
                        evaluacion = Evaluacion(
                            descripcion=f"Asistencia día {i+1}",
                            fecha=fecha_asistencia,
                            nota=nota_asistencia,
                            tipo_evaluacion_id=tipo_asistencia_diaria.id,
                            estudiante_ci=estudiante.ci,
                            materia_id=materia.id,
                            gestion_id=gestion_2.id
                        )
                        db.session.add(evaluacion)
                        evaluaciones_creadas += 1
                    
                    # Commit parcial cada 100 evaluaciones para evitar timeouts
                    if evaluaciones_creadas % 100 == 0:
                        db.session.commit()
                        print(f"  💾 Guardado parcial: {evaluaciones_creadas} evaluaciones")
                
                estudiantes_procesados += 1
                if estudiantes_procesados % 10 == 0:
                    print(f"  👥 Procesados: {estudiantes_procesados}/{len(estudiantes_2024)} estudiantes")
            
            # Commit final
            db.session.commit()
            print(f"\n✅ SEGUNDO TRIMESTRE COMPLETADO:")
            print(f"  📝 Evaluaciones creadas: {evaluaciones_creadas}")
            print(f"  👥 Estudiantes procesados: {estudiantes_procesados}")
            
            # Ahora calcular asistencias finales y notas finales
            calcular_notas_finales_optimizado(gestion_2.id, tipo_asistencia_final.id)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")
            return False

def calcular_notas_finales_optimizado(gestion_id, tipo_asistencia_final_id):
    """Calcula notas finales de forma optimizada"""
    print("\n📊 CALCULANDO NOTAS FINALES...")
    
    try:
        # Obtener estudiantes de 2024
        estudiantes_2024 = Estudiante.query.order_by(Estudiante.ci).limit(300).all()
        notas_actualizadas = 0
        
        for estudiante in estudiantes_2024:
            inscripcion = Inscripcion.query.filter_by(estudiante_ci=estudiante.ci).first()
            if not inscripcion:
                continue
                
            materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()
            
            for mc in materias_curso:
                materia = mc.materia
                
                # Calcular asistencia final
                asistencias_diarias = Evaluacion.query.filter_by(
                    estudiante_ci=estudiante.ci,
                    materia_id=materia.id,
                    gestion_id=gestion_id,
                    tipo_evaluacion_id=1  # Asistencia-Diaria
                ).all()
                
                if asistencias_diarias:
                    promedio_asistencia = sum(a.nota for a in asistencias_diarias) / len(asistencias_diarias)
                    
                    # Crear evaluación de asistencia final
                    asistencia_final = Evaluacion(
                        descripcion="Asistencia Final - Calculada automáticamente",
                        fecha=date(2024, 8, 30),
                        nota=promedio_asistencia,
                        tipo_evaluacion_id=tipo_asistencia_final_id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(asistencia_final)
                
                # Calcular nota final integral
                nota_final = calcular_nota_final_integral(estudiante.ci, gestion_id, materia.id)
                
                # Actualizar NotaFinal
                nota_final_obj = NotaFinal.query.filter_by(
                    estudiante_ci=estudiante.ci,
                    gestion_id=gestion_id,
                    materia_id=materia.id
                ).first()
                
                if nota_final_obj:
                    nota_final_obj.valor = nota_final
                    notas_actualizadas += 1
        
        db.session.commit()
        print(f"  ✅ Notas finales actualizadas: {notas_actualizadas}")
        
    except Exception as e:
        db.session.rollback()
        print(f"  ❌ Error al calcular notas finales: {str(e)}")

def calcular_nota_final_integral(estudiante_ci, gestion_id, materia_id):
    """Calcula la nota final integral usando las 4 dimensiones"""
    # Esta función implementa el cálculo correcto sin división
    # ser + decidir + hacer + saber = nota final (máximo 100)
    
    # Por simplicidad, calcularemos un promedio ponderado realista
    # En un sistema real, esto debería usar las dimensiones específicas
    
    evaluaciones = Evaluacion.query.filter_by(
        estudiante_ci=estudiante_ci,
        materia_id=materia_id,
        gestion_id=gestion_id
    ).all()
    
    if not evaluaciones:
        return 0.0
    
    # Calcular promedio simple y escalarlo a 100 puntos
    total_notas = sum(eval.nota for eval in evaluaciones)
    promedio = total_notas / len(evaluaciones)
    
    # Convertir a escala de 100 (asumiendo que las notas individuales están en escala de 35)
    nota_final = (promedio / 35) * 100
    return min(100.0, max(0.0, nota_final))

def generar_fecha_aleatoria(fecha_inicio, fecha_fin):
    """Genera una fecha aleatoria entre dos fechas"""
    dias_diferencia = (fecha_fin - fecha_inicio).days
    dias_aleatorios = random.randint(0, dias_diferencia)
    return fecha_inicio + timedelta(days=dias_aleatorios)

def generar_nota_realista(tipo_evaluacion):
    """Genera notas realistas según el tipo de evaluación"""
    if tipo_evaluacion == "examen":
        return round(random.uniform(14, 35), 1)
    elif tipo_evaluacion == "tarea":
        return round(random.uniform(21, 35), 1)
    elif tipo_evaluacion == "exposicion":
        return round(random.uniform(10.5, 15), 1)
    else:
        return round(random.uniform(17.5, 35), 1)

def generar_nota_asistencia():
    """Genera notas de asistencia usando escala de 15 puntos"""
    rand = random.random()
    if rand < 0.05:  # 5% faltas
        return 0
    elif rand < 0.12:  # 7% llegadas tarde
        return 5
    elif rand < 0.15:  # 3% con licencia
        return 10
    else:  # 85% presente
        return 15

if __name__ == "__main__":
    print("⏰ Iniciando completar segundo trimestre 2024...")
    if generar_evaluaciones_segundo_trimestre():
        print("🎉 ¡Segundo trimestre 2024 completado exitosamente!")
    else:
        print("❌ Error al completar segundo trimestre 2024")
