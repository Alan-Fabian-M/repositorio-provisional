#!/usr/bin/env python3
"""
Script para crear evaluaciones del segundo trimestre 2023
Se puede ejecutar en paralelo con los otros scripts de trimestres
"""

from app import create_app, db
from app.models.Gestion_Model import Gestion
from app.models.Evaluacion_Model import Evaluacion
from app.models.Inscripcion_Model import Inscripcion
from app.models.MateriaCurso_Model import MateriaCurso
from app.models.TipoEvaluacion_Model import TipoEvaluacion
from app.models.Materia_Model import Materia
from datetime import date, timedelta
import random
import requests
import json
import time

# Constantes
API_BASE_URL = "http://localhost:5000/api"
API_TOKEN = None

def login_admin():
    """Obtiene token de autenticación"""
    global API_TOKEN
    
    login_data = {
        "usuario": "admin",
        "contrasenia": "admin123"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
        response.raise_for_status()
        data = response.json()
        API_TOKEN = data.get("access_token")
        print(f"AUTENTICACION: Token obtenido exitosamente")
        return True
    except Exception as e:
        print(f"ERROR: No se pudo obtener token. {str(e)}")
        return False

def get_headers():
    """Retorna headers con token de autenticación"""
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

def crear_gestion_segundo_trimestre():
    """Crea la gestión del segundo trimestre 2023 si no existe"""
    app = create_app()
    
    with app.app_context():
        # Verificar si ya existe la gestión
        gestion = Gestion.query.filter_by(anio=2023, periodo="Segundo Trimestre").first()
        
        if gestion:
            print(f"AVISO: Gestión 2023 Segundo Trimestre ya existe (ID: {gestion.id})")
            return gestion.id
        
        # No existe, autenticarse y crear gestión mediante API
        if not API_TOKEN and not login_admin():
            print("ERROR: No se pudo autenticar. Revisa credenciales admin.")
            return None
        
        try:
            gestion_data = {
                "anio": 2023,
                "periodo": "Segundo Trimestre"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/gestion/with-notas",
                headers=get_headers(),
                json=gestion_data
            )
            
            response.raise_for_status()
            result = response.json()
            
            print(f"SUCESO: Gestión 2023 Segundo Trimestre creada (ID: {result['id']})")
            return result['id']
            
        except Exception as e:
            print(f"ERROR al crear gestión: {str(e)}")
            return None

def crear_evaluaciones_segundo_trimestre():
    """Crea evaluaciones para el segundo trimestre de 2023"""
    print("CREANDO EVALUACIONES SEGUNDO TRIMESTRE 2023")
    print("=" * 60)
    
    # Asegurarse de tener autenticación
    if not API_TOKEN and not login_admin():
        print("ERROR: No se pudo autenticar. Revisa credenciales admin.")
        return
    
    # Crear o obtener gestión
    gestion_id = crear_gestion_segundo_trimestre()
    if not gestion_id:
        print("ERROR: No se pudo obtener/crear la gestión del segundo trimestre 2023")
        return
    
    # Fechas del trimestre
    fecha_inicio = date(2023, 6, 1)
    fecha_fin = date(2023, 9, 30)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si ya existen evaluaciones para este trimestre
            evaluaciones_existentes = Evaluacion.query.filter_by(gestion_id=gestion_id).count()
            
            if evaluaciones_existentes > 0:
                print(f"AVISO: Ya existen {evaluaciones_existentes} evaluaciones para el segundo trimestre 2023")
                respuesta = input("¿Continuar creando evaluaciones? (s/n): ")
                if respuesta.lower() != 's':
                    return
            
            # Obtener inscripciones 2023
            inscripciones_2023 = Inscripcion.query.filter(
                Inscripcion.fecha >= date(2023, 1, 1),
                Inscripcion.fecha <= date(2023, 12, 31)
            ).all()
            
            if not inscripciones_2023:
                print("ERROR: No hay inscripciones para 2023. Ejecuta primero los scripts de preparación.")
                return
                
            print(f"Inscripciones 2023 encontradas: {len(inscripciones_2023)}")
            
            # Obtener tipos de evaluación
            tipos_evaluacion = TipoEvaluacion.query.all()
            
            if not tipos_evaluacion:
                print("ERROR: No hay tipos de evaluación definidos")
                return
                
            # Crear diccionario de tipos por nombre
            tipos_dic = {tipo.nombre: tipo for tipo in tipos_evaluacion}
            
            # Configuración de evaluaciones - Segundo trimestre tiene más exámenes
            config_evaluaciones = {
                'Asistencia-Diaria': {'cantidad': 30, 'min': 0, 'max': 15},
                'Examenes': {'cantidad': 3, 'min': 14, 'max': 35},  # Un examen más en el segundo trimestre
                'Tareas': {'cantidad': 5, 'min': 21, 'max': 35},    # Una tarea más en el segundo trimestre
                'Exposiciones': {'cantidad': 1, 'min': 10, 'max': 15},
                'Participacion': {'cantidad': 2, 'min': 10, 'max': 15}
            }
            
            # Contador para estadísticas
            evaluaciones_creadas = 0
            
            # Para cada inscripción
            for idx, inscripcion in enumerate(inscripciones_2023):
                estudiante_ci = inscripcion.estudiante_ci
                curso_id = inscripcion.curso_id
                
                # Obtener materias del curso
                materias_curso = MateriaCurso.query.filter_by(curso_id=curso_id).all()
                
                # Para cada materia del curso
                for materia_curso in materias_curso:
                    materia_id = materia_curso.materia_id
                    
                    # Para cada tipo de evaluación
                    for tipo_nombre, config in config_evaluaciones.items():
                        if tipo_nombre not in tipos_dic:
                            continue
                            
                        tipo_obj = tipos_dic[tipo_nombre]
                        
                        # Caso especial para Participación (solo 30% de estudiantes)
                        if tipo_nombre == 'Participacion' and random.random() > 0.3:
                            continue
                        
                        # Crear evaluaciones según la cantidad configurada
                        for i in range(config['cantidad']):
                            # Generar fecha aleatoria dentro del trimestre
                            dias_trimestre = (fecha_fin - fecha_inicio).days
                            fecha_random = fecha_inicio + timedelta(days=random.randint(0, dias_trimestre))
                            
                            # Generar nota aleatoria
                            if tipo_nombre == 'Asistencia-Diaria':
                                # Para asistencia usamos valores específicos
                                nota = random.choice([0, 5, 10, 15])
                                # 80% probabilidad de estar presente (15 puntos)
                                if random.random() < 0.8:
                                    nota = 15
                            else:
                                # Para otras evaluaciones generamos entre min y max
                                nota = round(random.uniform(config['min'], config['max']), 1)
                            
                            # Crear evaluación
                            evaluacion_data = {
                                "descripcion": f"{tipo_nombre} #{i+1} - 2023 T2",
                                "fecha": fecha_random.strftime("%Y-%m-%d"),
                                "nota": nota,
                                "tipo_evaluacion_id": tipo_obj.id,
                                "estudiante_ci": estudiante_ci,
                                "materia_id": materia_id,
                                "gestion_id": gestion_id
                            }
                            
                            try:
                                # Usar directamente SQLAlchemy en lugar de la API para mayor velocidad
                                evaluacion = Evaluacion(
                                    descripcion=evaluacion_data["descripcion"],
                                    fecha=fecha_random,
                                    nota=nota,
                                    tipo_evaluacion_id=tipo_obj.id,
                                    estudiante_ci=estudiante_ci,
                                    materia_id=materia_id,
                                    gestion_id=gestion_id
                                )
                                
                                db.session.add(evaluacion)
                                evaluaciones_creadas += 1
                                
                                # Commit cada 1000 evaluaciones para evitar sobrecarga de memoria
                                if evaluaciones_creadas % 1000 == 0:
                                    db.session.commit()
                                    print(f"  Progreso: {evaluaciones_creadas} evaluaciones creadas...")
                                
                            except Exception as e:
                                print(f"ERROR al crear evaluación: {str(e)}")
                
                # Mostrar progreso por estudiante
                if (idx + 1) % 20 == 0 or idx == len(inscripciones_2023) - 1:
                    print(f"  Procesados {idx + 1}/{len(inscripciones_2023)} estudiantes")
            
            # Commit final
            db.session.commit()
            
            # Estadísticas finales
            print("\nRESUMEN SEGUNDO TRIMESTRE 2023:")
            print("-" * 40)
            print(f"Total evaluaciones creadas: {evaluaciones_creadas}")
            
            # Estadísticas por tipo
            print("\nESTADÍSTICAS POR TIPO:")
            for tipo_nombre in config_evaluaciones.keys():
                if tipo_nombre in tipos_dic:
                    tipo_id = tipos_dic[tipo_nombre].id
                    count = Evaluacion.query.filter_by(
                        gestion_id=gestion_id,
                        tipo_evaluacion_id=tipo_id
                    ).count()
                    print(f"  - {tipo_nombre}: {count} evaluaciones")
            
            print("\nSEGUNDO TRIMESTRE 2023 COMPLETADO!")
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR general: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    crear_evaluaciones_segundo_trimestre()
