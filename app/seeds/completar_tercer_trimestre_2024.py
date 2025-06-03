#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPLETAR TERCER TRIMESTRE 2024
Crea la gestión y genera evaluaciones realistas para el tercer trimestre de 2024
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
from app.models.NotaEstimada_Model import NotaEstimada
from app.extensions import db

def crear_tercer_trimestre_2024():
    """Crea la gestión y evaluaciones para el tercer trimestre 2024"""
    app = create_app()
    with app.app_context():
        try:
            print("🏫 CREANDO TERCER TRIMESTRE 2024")
            print("=" * 50)
            
            # Verificar si ya existe
            gestion_existente = Gestion.query.filter_by(anio=2024, periodo="Tercer Trimestre").first()
            if gestion_existente:
                print(f"⚠️ Ya existe el Tercer Trimestre 2024 (ID: {gestion_existente.id})")
                evaluaciones_existentes = Evaluacion.query.filter_by(gestion_id=gestion_existente.id).count()
                if evaluaciones_existentes > 0:
                    print(f"Ya tiene {evaluaciones_existentes} evaluaciones. ¿Continuar? (y/n)")
                    respuesta = input().lower()
                    if respuesta != 'y':
                        return False
                gestion_3 = gestion_existente
            else:
                # Crear la gestión del tercer trimestre
                gestion_3 = Gestion(anio=2024, periodo="Tercer Trimestre")
                db.session.add(gestion_3)
                db.session.commit()
                print(f"✅ Gestión creada: Tercer Trimestre (ID: {gestion_3.id})")
                
                # Crear estructura base de notas
                crear_estructura_notas_base(gestion_3.id)
            
            # Fechas del tercer trimestre
            fecha_inicio = date(2024, 9, 2)
            fecha_fin = date(2024, 11, 29)
            
            # Generar evaluaciones
            generar_evaluaciones_tercer_trimestre(gestion_3.id, fecha_inicio, fecha_fin)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")
            return False

def crear_estructura_notas_base(gestion_id):
    """Crea NotaFinal y NotaEstimada para todos los estudiantes de 2024"""
    print("📊 Creando estructura base de notas...")
    
    try:
        estudiantes_2024 = Estudiante.query.order_by(Estudiante.ci).limit(300).all()
        notas_creadas = 0
        
        for estudiante in estudiantes_2024:
            inscripcion = Inscripcion.query.filter_by(estudiante_ci=estudiante.ci).first()
            if not inscripcion or not inscripcion.curso:
                continue
            
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
                    razon_estimacion="Tercer Trimestre 2024 - estructura inicial",
                    estudiante_ci=estudiante.ci,
                    gestion_id=gestion_id,
                    materia_id=mc.materia.id
                )
                db.session.add(nota_estimada)
                notas_creadas += 2
        
        db.session.commit()
        print(f"  ✅ Estructura de notas creada: {notas_creadas} registros")
        
    except Exception as e:
        db.session.rollback()
        print(f"  ❌ Error al crear estructura base: {str(e)}")

def generar_evaluaciones_tercer_trimestre(gestion_id, fecha_inicio, fecha_fin):
    """Genera evaluaciones para el tercer trimestre 2024"""
    print("📝 Generando evaluaciones del tercer trimestre...")
    
    try:
        # Obtener tipos de evaluación
        tipo_examen = TipoEvaluacion.query.filter_by(nombre='Examenes').first()
        tipo_tarea = TipoEvaluacion.query.filter_by(nombre='Tareas').first()
        tipo_exposicion = TipoEvaluacion.query.filter_by(nombre='Exposiciones').first()
        tipo_asistencia_diaria = TipoEvaluacion.query.filter_by(nombre='Asistencia-Diaria').first()
        tipo_asistencia_final = TipoEvaluacion.query.filter_by(nombre='Asistencia-Final').first()
        
        if not all([tipo_examen, tipo_tarea, tipo_exposicion, tipo_asistencia_diaria, tipo_asistencia_final]):
            print("❌ No se encontraron todos los tipos de evaluación")
            return False
        
        # Obtener estudiantes de 2024
        estudiantes_2024 = Estudiante.query.order_by(Estudiante.ci).limit(300).all()
        print(f"📚 Procesando {len(estudiantes_2024)} estudiantes...")
        
        evaluaciones_creadas = 0
        estudiantes_procesados = 0
        
        for estudiante in estudiantes_2024:
            inscripcion = Inscripcion.query.filter_by(estudiante_ci=estudiante.ci).first()
            if not inscripcion or not inscripcion.curso:
                continue
            
            materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()
            
            for mc in materias_curso:
                materia = mc.materia
                
                # Verificar si ya tiene evaluaciones
                eval_existente = Evaluacion.query.filter_by(
                    estudiante_ci=estudiante.ci,
                    materia_id=materia.id,
                    gestion_id=gestion_id
                ).first()
                
                if eval_existente:
                    continue  # Ya tiene evaluaciones, saltar
                
                # 1. EXÁMENES (2-3 por trimestre)
                num_examenes = random.randint(2, 3)
                for i in range(num_examenes):
                    fecha_examen = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                    nota_examen = generar_nota_realista("examen")
                    
                    evaluacion = Evaluacion(
                        descripcion=f"Examen {i+1} - Tercer Trimestre",
                        fecha=fecha_examen,
                        nota=nota_examen,
                        tipo_evaluacion_id=tipo_examen.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(evaluacion)
                    evaluaciones_creadas += 1
                
                # 2. TAREAS (4-6 por trimestre)
                num_tareas = random.randint(4, 6)
                for i in range(num_tareas):
                    fecha_tarea = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                    nota_tarea = generar_nota_realista("tarea")
                    
                    evaluacion = Evaluacion(
                        descripcion=f"Tarea {i+1} - Tercer Trimestre",
                        fecha=fecha_tarea,
                        nota=nota_tarea,
                        tipo_evaluacion_id=tipo_tarea.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(evaluacion)
                    evaluaciones_creadas += 1
                
                # 3. EXPOSICIONES (1-2 por trimestre)
                num_exposiciones = random.randint(1, 2)
                for i in range(num_exposiciones):
                    fecha_exposicion = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                    nota_exposicion = generar_nota_realista("exposicion")
                    
                    evaluacion = Evaluacion(
                        descripcion=f"Exposición {i+1} - Tercer Trimestre",
                        fecha=fecha_exposicion,
                        nota=nota_exposicion,
                        tipo_evaluacion_id=tipo_exposicion.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
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
                        gestion_id=gestion_id
                    )
                    db.session.add(evaluacion)
                    evaluaciones_creadas += 1
                
                # Commit parcial cada 100 evaluaciones
                if evaluaciones_creadas % 100 == 0:
                    db.session.commit()
                    print(f"  💾 Guardado parcial: {evaluaciones_creadas} evaluaciones")
            
            estudiantes_procesados += 1
            if estudiantes_procesados % 10 == 0:
                print(f"  👥 Procesados: {estudiantes_procesados}/{len(estudiantes_2024)} estudiantes")
        
        # Commit final
        db.session.commit()
        print(f"\n✅ EVALUACIONES COMPLETADAS:")
        print(f"  📝 Evaluaciones creadas: {evaluaciones_creadas}")
        print(f"  👥 Estudiantes procesados: {estudiantes_procesados}")
        
        # Calcular asistencias finales y notas finales
        calcular_notas_finales_optimizado(gestion_id, tipo_asistencia_final.id)
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al generar evaluaciones: {str(e)}")
        return False

def calcular_notas_finales_optimizado(gestion_id, tipo_asistencia_final_id):
    """Calcula notas finales de forma optimizada"""
    print("\n📊 CALCULANDO NOTAS FINALES...")
    
    try:
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
                        fecha=date(2024, 11, 29),
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
    """Calcula la nota final integral"""
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
    
    # Convertir a escala de 100
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
    print("⏰ Iniciando creación del tercer trimestre 2024...")
    if crear_tercer_trimestre_2024():
        print("🎉 ¡Tercer trimestre 2024 completado exitosamente!")
    else:
        print("❌ Error al crear tercer trimestre 2024")
