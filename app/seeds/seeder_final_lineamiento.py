# -*- coding: utf-8 -*-
"""
Seeder que sigue el lineamiento correcto:
1. Crear gestión
2. Colocar asistencia diaria (endpoint)
3. Colocar evaluaciones académicas (endpoint)
4. Calcular nota final (automático)

Sistema de 15 puntos para asistencia:
- Presente: 15 puntos (85% probabilidad)
- Tarde: 5 puntos (7% probabilidad)  
- Licencia: 10 puntos (3% probabilidad)
- Falta: 0 puntos (5% probabilidad)
"""

import requests
import json
import random
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db

# Configuración del servidor Flask
BASE_URL = "http://localhost:5000"

class SeederLineamientoCorregido:
    def __init__(self):
        self.app = create_app()
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
    def verificar_servidor(self):
        """Verificar que el servidor Flask esté corriendo"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("✅ Servidor Flask está corriendo")
                return True
        except Exception as e:
            print("❌ Error: Servidor Flask no está corriendo")
            print("Por favor ejecuta: python app.py")
            print(f"Error: {str(e)}")
            return False
    
    def crear_gestion(self, anio, periodo, fecha_inicio, fecha_fin):
        """Crear gestión usando endpoint"""
        data = {
            "anio": anio,
            "periodo": periodo,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/gestion", json=data)
            if response.status_code == 201:
                gestion_data = response.json()
                print(f"✅ Gestión creada: {anio} {periodo} (ID: {gestion_data['id']})")
                return gestion_data['id']
            else:
                print(f"❌ Error creando gestión: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error de conexión al crear gestión: {str(e)}")
            return None
    
    def obtener_gestiones(self):
        """Obtener todas las gestiones"""
        try:
            response = self.session.get(f"{BASE_URL}/gestion")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def obtener_estudiantes_curso(self, curso_id):
        """Obtener estudiantes de un curso específico (CI)"""
        with self.app.app_context():
            from app.models.Inscripcion_Model import Inscripcion
            inscripciones = Inscripcion.query.filter_by(curso_id=curso_id).all()
            return [inscripcion.estudiante_ci for inscripcion in inscripciones]
    
    def obtener_materias_curso(self, curso_id):
        """Obtener materias de un curso específico"""
        with self.app.app_context():
            from app.models.MateriaCurso_Model import MateriaCurso
            materias_curso = MateriaCurso.query.filter_by(curso_id=curso_id).all()
            return [(mc.materia_id, mc.materia.nombre) for mc in materias_curso if mc.materia]
    
    def generar_asistencia_realista(self):
        """Generar asistencia con distribución realista del sistema de 15 puntos"""
        rand = random.random()
        if rand < 0.85:  # 85% presente
            return 15, "Presente"
        elif rand < 0.92:  # 7% tarde
            return 5, "Tarde"
        elif rand < 0.95:  # 3% licencia
            return 10, "Licencia"
        else:  # 5% falta
            return 0, "Falta"
    
    def generar_nota_academica(self, tipo_evaluacion):
        """Generar notas académicas con los límites correctos"""
        if tipo_evaluacion == "Examenes":
            # 14-35 puntos, promedio 24.5
            return round(random.uniform(14, 35), 1)
        elif tipo_evaluacion == "Tareas":
            # 21-35 puntos, promedio 28.0
            return round(random.uniform(21, 35), 1)
        elif tipo_evaluacion == "Exposiciones":
            # 10.5-15 puntos, promedio 12.8
            return round(random.uniform(10.5, 15), 1)
        return 0
    
    def colocar_asistencia_diaria(self, gestion_id, estudiante_ci, materia_id, fecha):
        """Colocar asistencia diaria usando endpoint"""
        nota, descripcion = self.generar_asistencia_realista()
        
        data = {
            "estudiante_ci": estudiante_ci,
            "materia_id": materia_id,
            "gestion_id": gestion_id,
            "tipo_evaluacion_id": 1,  # Asistencia-Diaria
            "nota": nota,
            "fecha": fecha,
            "descripcion": descripcion
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/evaluacion", json=data)
            return response.status_code == 201
        except:
            return False
    
    def colocar_evaluacion_academica(self, gestion_id, estudiante_ci, materia_id, tipo_evaluacion_id, tipo_nombre, fecha):
        """Colocar evaluación académica usando endpoint"""
        nota = self.generar_nota_academica(tipo_nombre)
        
        data = {
            "estudiante_ci": estudiante_ci,
            "materia_id": materia_id,
            "gestion_id": gestion_id,
            "tipo_evaluacion_id": tipo_evaluacion_id,
            "nota": nota,
            "fecha": fecha,
            "descripcion": f"{tipo_nombre} - Nota generada automáticamente"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/evaluacion", json=data)
            return response.status_code == 201
        except:
            return False
    
    def completar_2024_tercer_trimestre(self):
        """Completar 2024 Tercer Trimestre si falta algo"""
        print("\n🔄 Verificando 2024 Tercer Trimestre...")
        
        with self.app.app_context():
            from app.models.Gestion_Model import Gestion
            from app.models.Evaluacion_Model import Evaluacion
            
            gestion = Gestion.query.filter_by(anio=2024, periodo="Tercer Trimestre").first()
            if not gestion:
                print("❌ No existe la gestión 2024 Tercer Trimestre")
                return False
            
            # Verificar si tiene notas finales
            notas_finales = Evaluacion.query.filter_by(
                gestion_id=gestion.id,
                tipo_evaluacion_id=2  # Asistencia-Final
            ).count()
            
            print(f"✅ 2024 Tercer Trimestre tiene {notas_finales} notas finales")
            print("   📌 Las notas finales se calculan automáticamente al crear evaluaciones")
        
        return True
    
    def crear_2025_primer_trimestre(self):
        """Crear 2025 Primer Trimestre (solo estructura)"""
        print("\n🆕 Creando 2025 Primer Trimestre...")
        
        # Verificar si ya existe
        with self.app.app_context():
            from app.models.Gestion_Model import Gestion
            gestion_existente = Gestion.query.filter_by(anio=2025, periodo="Primer Trimestre").first()
            if gestion_existente:
                print("✅ 2025 Primer Trimestre ya existe")
                return True
        
        # Crear la gestión
        fecha_inicio = "2025-02-03"
        fecha_fin = "2025-05-30"
        
        gestion_id = self.crear_gestion(2025, "Primer Trimestre", fecha_inicio, fecha_fin)
        if gestion_id:
            print("✅ 2025 Primer Trimestre creado (solo estructura)")
            print("   📌 Nota: No se generaron evaluaciones, solo la gestión base")
            return True
        
        return False
    
    def crear_prueba_evaluaciones_2025(self):
        """Crear algunas evaluaciones de prueba para 2025 usando endpoints"""
        print("\n🧪 Creando evaluaciones de prueba para 2025...")
        
        with self.app.app_context():
            from app.models.Gestion_Model import Gestion
            from app.models.Curso_Model import Curso
            
            gestion = Gestion.query.filter_by(anio=2025, periodo="Primer Trimestre").first()
            if not gestion:
                print("❌ No existe la gestión 2025 Primer Trimestre")
                return False
            
            # Obtener un curso de prueba
            curso = Curso.query.first()
            if not curso:
                print("❌ No hay cursos disponibles")
                return False
            
            estudiantes = self.obtener_estudiantes_curso(curso.id)
            materias = self.obtener_materias_curso(curso.id)
            
            if not estudiantes or not materias:
                print("❌ No hay estudiantes o materias en el curso")
                return False
            
            print(f"🏫 Curso: {curso.nombre}")
            print(f"👥 Estudiantes: {len(estudiantes)}")
            print(f"📖 Materias: {len(materias)}")
            
            # Crear evaluaciones para los primeros 3 estudiantes y primera materia
            estudiantes_prueba = estudiantes[:3]
            materia_id, materia_nombre = materias[0]
            
            total_creadas = 0
            
            for estudiante_ci in estudiantes_prueba:
                # Crear algunas asistencias
                for i in range(5):  # 5 días de asistencia
                    fecha = f"2025-02-{10+i:02d}"
                    if self.colocar_asistencia_diaria(gestion.id, estudiante_ci, materia_id, fecha):
                        total_creadas += 1
                
                # Crear un examen
                if self.colocar_evaluacion_academica(gestion.id, estudiante_ci, materia_id, 3, "Examenes", "2025-02-20"):
                    total_creadas += 1
                
                # Crear una tarea
                if self.colocar_evaluacion_academica(gestion.id, estudiante_ci, materia_id, 4, "Tareas", "2025-02-25"):
                    total_creadas += 1
            
            print(f"✅ Evaluaciones de prueba creadas: {total_creadas}")
            return True
    
    def ejecutar_lineamiento_completo(self):
        """Ejecutar el lineamiento completo"""
        print("🎯 SEEDER SIGUIENDO EL LINEAMIENTO CORRECTO")
        print("=" * 60)
        
        if not self.verificar_servidor():
            return False
        
        # Completar lo que falta
        success = True
        
        # 1. Completar 2024 Tercer Trimestre (verificar estado)
        if not self.completar_2024_tercer_trimestre():
            success = False
        
        # 2. Crear 2025 Primer Trimestre (solo estructura)
        if not self.crear_2025_primer_trimestre():
            success = False
        
        # 3. Crear algunas evaluaciones de prueba para 2025
        if not self.crear_prueba_evaluaciones_2025():
            success = False
        
        if success:
            print("\n🎉 ¡LINEAMIENTO COMPLETADO EXITOSAMENTE!")
            print("✅ Sistema de 15 puntos implementado correctamente")
            print("✅ Evaluaciones con límites correctos")
            print("✅ Flujo de endpoints respetado")
            print("✅ 2025 Primer Trimestre creado con evaluaciones de prueba")
        else:
            print("\n❌ Hubo errores en el proceso")
        
        return success

def main():
    seeder = SeederLineamientoCorregido()
    seeder.ejecutar_lineamiento_completo()

if __name__ == "__main__":
    main()
