#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CREAR GESTIÓN 2025 CON PROMOCIÓN DE ESTUDIANTES
Crea inscripciones 2025 con progresión de grados y estructura básica de notas
"""

import os
import sys
from datetime import date

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models.Estudiante_Model import Estudiante
from app.models.Inscripcion_Model import Inscripcion
from app.models.Curso_Model import Curso
from app.models.Materia_Model import Materia
from app.models.MateriaCurso_Model import MateriaCurso
from app.models.Gestion_Model import Gestion
from app.models.Evaluacion_Model import Evaluacion
from app.models.TipoEvaluacion_Model import TipoEvaluacion
from app.models.NotaFinal_Model import NotaFinal
from app.models.NotaEstimada_Model import NotaEstimada
from app.extensions import db

def crear_gestion_2025():
    """Crea la gestión 2025 con promoción de estudiantes y estructura básica"""
    app = create_app()
    with app.app_context():
        try:
            print("🏫 CREANDO GESTIÓN 2025 CON PROMOCIÓN DE ESTUDIANTES")
            print("=" * 60)
            
            # Verificar si ya existe gestión 2025
            gestion_existente = Gestion.query.filter_by(anio=2025).first()
            if gestion_existente:
                print(f"⚠️ Ya existe una gestión 2025 (ID: {gestion_existente.id})")
                inscripciones_2025 = Inscripcion.query.filter_by(fecha=date(2025, 2, 1)).count()
                if inscripciones_2025 > 0:
                    print(f"Ya existen {inscripciones_2025} inscripciones 2025. ¿Continuar? (y/n)")
                    respuesta = input().lower()
                    if respuesta != 'y':
                        return False
            
            # 1. Crear inscripciones 2025 con promoción de grados
            crear_inscripciones_2025_con_promocion()
            
            # 2. Crear gestión 2025
            if not gestion_existente:
                gestion_2025 = Gestion(anio=2025, periodo="Primer semestre")
                db.session.add(gestion_2025)
                db.session.commit()
                print(f"✅ Gestión 2025 creada (ID: {gestion_2025.id})")
            else:
                gestion_2025 = gestion_existente
                print(f"✅ Usando gestión 2025 existente (ID: {gestion_2025.id})")
            
            # 3. Crear estructura básica de notas para 2025
            crear_estructura_notas_2025(gestion_2025.id)
            
            # 4. Mostrar resumen
            mostrar_resumen_2025()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")
            return False

def crear_inscripciones_2025_con_promocion():
    """Crea inscripciones para 2025 promoviendo a estudiantes de 2024"""
    print("\n📈 PASO 1: PROMOCIÓN DE ESTUDIANTES 2024 → 2025")
    print("-" * 50)
    
    try:
        # Información de cursos
        curso_info = {
            1: "1A", 2: "1B", 3: "2A", 4: "2B", 5: "3A", 6: "3B",
            7: "4A", 8: "4B", 9: "5A", 10: "5B", 11: "6A", 12: "6B"
        }
        
        # Verificar inscripciones 2025 existentes
        inscripciones_2025_existentes = Inscripcion.query.filter_by(fecha=date(2025, 2, 1)).count()
        if inscripciones_2025_existentes > 0:
            print(f"Ya existen {inscripciones_2025_existentes} inscripciones 2025")
            return
        
        # Obtener todas las inscripciones de 2024
        inscripciones_2024 = Inscripcion.query.filter_by(fecha=date(2024, 2, 1)).all()
        estudiantes_2024 = [insc.estudiante_ci for insc in inscripciones_2024]
        
        print(f"Promoviendo {len(inscripciones_2024)} estudiantes de 2024...")
        
        inscripciones_2025 = []
        id_counter = 301  # Continuar desde donde terminaron las inscripciones 2024
        estudiantes_promovidos = 0
        estudiantes_graduados = 0
        
        # PASO 1A: Promover estudiantes de 2024 al siguiente grado
        for inscripcion_2024 in inscripciones_2024:
            curso_2024 = inscripcion_2024.curso_id
            
            # Los de 6° se gradúan (no se inscriben en 2025)
            if curso_2024 in [11, 12]:  # 6A y 6B
                estudiantes_graduados += 1
                continue
            
            # Mapeo de promoción: 1A→2A, 1B→2B, 2A→3A, 2B→3B, etc.
            nuevo_curso = curso_2024 + 2
            
            if nuevo_curso > 12:  # Verificación adicional
                continue
            
            descripcion = f"Inscripción año escolar 2025 - Promovido a {curso_info[nuevo_curso]}"
            
            inscripcion_2025 = Inscripcion(
                id=id_counter,
                descripcion=descripcion,
                fecha=date(2025, 2, 1),
                estudiante_ci=inscripcion_2024.estudiante_ci,
                curso_id=nuevo_curso
            )
            
            inscripciones_2025.append(inscripcion_2025)
            id_counter += 1
            estudiantes_promovidos += 1
        
        print(f"  ✅ Estudiantes promovidos: {estudiantes_promovidos}")
        print(f"  🎓 Estudiantes graduados: {estudiantes_graduados}")
        
        # PASO 1B: Agregar estudiantes nuevos (301-600) para llenar espacios
        print("\n🆕 PASO 1B: INSCRIBIENDO ESTUDIANTES NUEVOS")
        print("-" * 50)
        
        # Contar espacios disponibles por curso
        estudiantes_por_curso_2025 = {i: 0 for i in range(1, 13)}
        for insc in inscripciones_2025:
            estudiantes_por_curso_2025[insc.curso_id] += 1
        
        # Calcular espacios disponibles (máximo 25 por curso)
        espacios_por_curso = {}
        for curso_id in range(1, 13):
            espacios_por_curso[curso_id] = max(0, 25 - estudiantes_por_curso_2025[curso_id])
        
        print(f"Espacios disponibles por curso: {espacios_por_curso}")
        
        # Priorizar llenar 1° con estudiantes nuevos
        cursos_prioritarios = [1, 2]  # 1A y 1B primero
        cursos_restantes = [i for i in range(3, 13) if espacios_por_curso[i] > 0]
        orden_cursos = cursos_prioritarios + cursos_restantes
        
        # Obtener estudiantes nuevos (301-600)
        todos_estudiantes = Estudiante.query.order_by(Estudiante.ci).all()
        estudiantes_nuevos = [est for est in todos_estudiantes if est.ci not in estudiantes_2024]
        
        print(f"Estudiantes nuevos disponibles: {len(estudiantes_nuevos)}")
        
        estudiante_index = 0
        estudiantes_nuevos_inscritos = 0
        
        for curso_id in orden_cursos:
            espacios_disponibles = espacios_por_curso[curso_id]
            
            for _ in range(espacios_disponibles):
                if estudiante_index >= len(estudiantes_nuevos):
                    break
                
                estudiante = estudiantes_nuevos[estudiante_index]
                
                descripcion = f"Inscripción año escolar 2025 - Curso {curso_info[curso_id]}"
                
                inscripcion_2025 = Inscripcion(
                    id=id_counter,
                    descripcion=descripcion,
                    fecha=date(2025, 2, 1),
                    estudiante_ci=estudiante.ci,
                    curso_id=curso_id
                )
                
                inscripciones_2025.append(inscripcion_2025)
                id_counter += 1
                estudiante_index += 1
                estudiantes_nuevos_inscritos += 1
            
            if estudiante_index >= len(estudiantes_nuevos):
                break
        
        print(f"  ✅ Estudiantes nuevos inscritos: {estudiantes_nuevos_inscritos}")
        
        # Guardar todas las inscripciones 2025
        for inscripcion in inscripciones_2025:
            db.session.add(inscripcion)
        
        db.session.commit()
        print(f"\n✅ INSCRIPCIONES 2025 CREADAS: {len(inscripciones_2025)} inscripciones")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear inscripciones 2025: {str(e)}")
        raise

def crear_estructura_notas_2025(gestion_id):
    """Crea estructura básica de notas para todos los estudiantes de 2025"""
    print("\n📊 PASO 2: CREANDO ESTRUCTURA DE NOTAS 2025")
    print("-" * 50)
    
    try:
        # Obtener todas las inscripciones de 2025
        inscripciones_2025 = Inscripcion.query.filter_by(fecha=date(2025, 2, 1)).all()
        
        print(f"Creando estructura para {len(inscripciones_2025)} estudiantes...")
        
        # Obtener tipo de evaluación para asistencia básica
        tipo_asistencia_final = TipoEvaluacion.query.filter_by(nombre='Asistencia-Final').first()
        
        notas_finales_creadas = 0
        notas_estimadas_creadas = 0
        evaluaciones_basicas_creadas = 0
        
        for inscripcion in inscripciones_2025:
            estudiante = inscripcion.estudiante
            if not estudiante:
                continue
            
            # Obtener materias del curso
            materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()
            
            for mc in materias_curso:
                materia = mc.materia
                if not materia:
                    continue
                
                # Verificar si ya existe NotaFinal
                nota_final_existente = NotaFinal.query.filter_by(
                    estudiante_ci=estudiante.ci,
                    gestion_id=gestion_id,
                    materia_id=materia.id
                ).first()
                
                if not nota_final_existente:
                    # Crear NotaFinal
                    nota_final = NotaFinal(
                        valor=0.0,
                        estudiante_ci=estudiante.ci,
                        gestion_id=gestion_id,
                        materia_id=materia.id
                    )
                    db.session.add(nota_final)
                    notas_finales_creadas += 1
                
                # Verificar si ya existe NotaEstimada
                nota_estimada_existente = NotaEstimada.query.filter_by(
                    estudiante_ci=estudiante.ci,
                    gestion_id=gestion_id,
                    materia_id=materia.id
                ).first()
                
                if not nota_estimada_existente:
                    # Crear NotaEstimada
                    nota_estimada = NotaEstimada(
                        valor_estimado=0.0,
                        razon_estimacion="Gestión 2025 - estructura básica",
                        estudiante_ci=estudiante.ci,
                        gestion_id=gestion_id,
                        materia_id=materia.id
                    )
                    db.session.add(nota_estimada)
                    notas_estimadas_creadas += 1
                
                # Verificar si ya existe evaluación básica
                evaluacion_existente = Evaluacion.query.filter_by(
                    estudiante_ci=estudiante.ci,
                    materia_id=materia.id,
                    gestion_id=gestion_id
                ).first()
                
                if not evaluacion_existente and tipo_asistencia_final:
                    # Crear evaluación básica de asistencia
                    evaluacion = Evaluacion(
                        descripcion="Asistencia final - estructura básica",
                        fecha=date.today(),
                        nota=0.0,
                        tipo_evaluacion_id=tipo_asistencia_final.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(evaluacion)
                    evaluaciones_basicas_creadas += 1
        
        db.session.commit()
        print(f"  ✅ NotaFinal creadas: {notas_finales_creadas}")
        print(f"  ✅ NotaEstimada creadas: {notas_estimadas_creadas}")
        print(f"  ✅ Evaluaciones básicas: {evaluaciones_basicas_creadas}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear estructura de notas: {str(e)}")
        raise

def mostrar_resumen_2025():
    """Muestra un resumen de la gestión 2025 creada"""
    print("\n📈 RESUMEN GESTIÓN 2025")
    print("=" * 50)
    
    try:
        # Información de cursos
        curso_info = {
            1: "1A", 2: "1B", 3: "2A", 4: "2B", 5: "3A", 6: "3B",
            7: "4A", 8: "4B", 9: "5A", 10: "5B", 11: "6A", 12: "6B"
        }
        
        inscripciones_2025 = Inscripcion.query.filter_by(fecha=date(2025, 2, 1)).all()
        gestion_2025 = Gestion.query.filter_by(anio=2025).first()
        
        # Contar estudiantes por curso
        estudiantes_por_curso = {i: 0 for i in range(1, 13)}
        for insc in inscripciones_2025:
            estudiantes_por_curso[insc.curso_id] += 1
        
        print(f"Total inscripciones 2025: {len(inscripciones_2025)}")
        print(f"Gestión ID: {gestion_2025.id if gestion_2025 else 'No encontrada'}")
        
        print("\nDistribución por curso:")
        for curso_id in range(1, 13):
            cantidad = estudiantes_por_curso[curso_id]
            print(f"  {curso_info[curso_id]}: {cantidad} estudiantes")
        
        if gestion_2025:
            notas_finales = NotaFinal.query.filter_by(gestion_id=gestion_2025.id).count()
            notas_estimadas = NotaEstimada.query.filter_by(gestion_id=gestion_2025.id).count()
            evaluaciones = Evaluacion.query.filter_by(gestion_id=gestion_2025.id).count()
            
            print(f"\nEstructura de notas:")
            print(f"  NotaFinal: {notas_finales}")
            print(f"  NotaEstimada: {notas_estimadas}")
            print(f"  Evaluaciones: {evaluaciones}")
        
        print("\n🎯 GESTIÓN 2025 LISTA PARA USO")
        print("Los estudiantes ahora pueden recibir evaluaciones en la nueva gestión")
        
    except Exception as e:
        print(f"❌ Error al mostrar resumen: {str(e)}")

if __name__ == "__main__":
    print("⏰ Iniciando creación de gestión 2025...")
    if crear_gestion_2025():
        print("\n🎉 ¡Gestión 2025 creada exitosamente!")
        print("Los estudiantes han sido promovidos correctamente al siguiente grado")
    else:
        print("❌ Error al crear gestión 2025")
