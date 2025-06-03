#!/usr/bin/env python3
"""
Script para crear gestiones 2023 con configuración inicial de notas
"""

from app import create_app, db
from app.models.Gestion_Model import Gestion
from app.models.TipoEvaluacion_Model import TipoEvaluacion
from app.models.EvaluacionIntegral_Model import EvaluacionIntegral

def crear_gestiones_2023_con_notas():
    """Crea gestiones para el año 2023 y configura tipos de evaluación si es necesario"""
    app = create_app()
    
    with app.app_context():
        print("CREANDO GESTIONES 2023 Y VERIFICANDO TIPOS DE EVALUACIÓN")
        print("=" * 60)
        
        try:
            # Parte 1: Crear las gestiones para 2023
            print("\n1. Creando gestiones para 2023...")
            gestiones_2023 = [
                {
                    'anio': 2023,
                    'periodo': '1'  # Primer trimestre
                },
                {
                    'anio': 2023,
                    'periodo': '2'  # Segundo trimestre
                },
                {
                    'anio': 2023,
                    'periodo': '3'  # Tercer trimestre
                }
            ]
            
            gestiones_creadas = 0
            gestiones_ids = []
            
            for gestion_data in gestiones_2023:
                # Verificar si ya existe
                gestion_existente = Gestion.query.filter_by(
                    anio=gestion_data['anio'],
                    periodo=gestion_data['periodo']
                ).first()
                
                if not gestion_existente:
                    nueva_gestion = Gestion(
                        anio=gestion_data['anio'],
                        periodo=gestion_data['periodo']
                    )
                    db.session.add(nueva_gestion)
                    db.session.commit()  # Commit inmediato para obtener el ID
                    gestiones_creadas += 1
                    print(f"OK: Creada gestión {gestion_data['anio']} trimestre {gestion_data['periodo']} con ID {nueva_gestion.id}")
                    gestiones_ids.append(nueva_gestion.id)
                else:
                    print(f"YA EXISTE: Gestión {gestion_data['anio']} trimestre {gestion_data['periodo']} (ID: {gestion_existente.id})")
                    gestiones_ids.append(gestion_existente.id)
            
            # Parte 2: Verificar y crear los tipos de evaluación básicos si no existen
            print("\n2. Verificando tipos de evaluación...")
            tipos_evaluacion = [
                # Ser (15%)
                {"nombre": "Asistencia", "dimension": "ser", "descripcion": "Control de asistencia a clases", "porcentaje": 10},
                {"nombre": "Participación", "dimension": "ser", "descripcion": "Participación activa en clase", "porcentaje": 5},
                
                # Saber (35%)
                {"nombre": "Examen escrito", "dimension": "saber", "descripcion": "Evaluación de conocimientos teóricos", "porcentaje": 20},
                {"nombre": "Prueba corta", "dimension": "saber", "descripcion": "Evaluación rápida de conceptos", "porcentaje": 15},
                
                # Hacer (35%)
                {"nombre": "Práctica", "dimension": "hacer", "descripcion": "Ejercicios prácticos en clase", "porcentaje": 15},
                {"nombre": "Tarea", "dimension": "hacer", "descripcion": "Tareas para realizar en casa", "porcentaje": 20},
                
                # Decidir (15%)
                {"nombre": "Proyecto", "dimension": "decidir", "descripcion": "Proyecto integrador de conocimientos", "porcentaje": 10},
                {"nombre": "Exposición", "dimension": "decidir", "descripcion": "Presentación oral de un tema", "porcentaje": 5}
            ]
            
            tipos_creados = 0
            
            for tipo_data in tipos_evaluacion:
                tipo_existente = TipoEvaluacion.query.filter_by(
                    nombre=tipo_data["nombre"],
                    dimension=tipo_data["dimension"]
                ).first()
                
                if not tipo_existente:
                    nuevo_tipo = TipoEvaluacion(
                        nombre=tipo_data["nombre"],
                        dimension=tipo_data["dimension"],
                        descripcion=tipo_data["descripcion"],
                        porcentaje=tipo_data["porcentaje"]
                    )
                    db.session.add(nuevo_tipo)
                    tipos_creados += 1
            
            if tipos_creados > 0:
                db.session.commit()
                print(f"Se crearon {tipos_creados} nuevos tipos de evaluación.")
            else:
                print("Todos los tipos de evaluación necesarios ya existen.")
                
            # Parte 3: Verificar la evaluación integral
            print("\n3. Verificando evaluación integral...")
            dimensiones = ["ser", "saber", "hacer", "decidir"]
            porcentajes = {"ser": 15, "saber": 35, "hacer": 35, "decidir": 15}
            
            for dimension in dimensiones:
                eval_integral = EvaluacionIntegral.query.filter_by(dimension=dimension).first()
                if not eval_integral:
                    nuevo_integral = EvaluacionIntegral(
                        dimension=dimension,
                        porcentaje=porcentajes[dimension],
                        descripcion=f"Dimensión {dimension.capitalize()} ({porcentajes[dimension]}%)"
                    )
                    db.session.add(nuevo_integral)
                    print(f"Creada evaluación integral para dimensión {dimension}: {porcentajes[dimension]}%")
                else:
                    print(f"Ya existe evaluación integral para dimensión {dimension}: {eval_integral.porcentaje}%")
            
            db.session.commit()
            
            # Resumen final
            print(f"\nRESUMEN:")
            print(f"- Gestiones creadas: {gestiones_creadas}")
            print(f"- IDs de gestiones 2023: {gestiones_ids}")
            print(f"- Tipos de evaluación creados: {tipos_creados}")
            
            # Verificar todas las gestiones 2023
            todas_gestiones_2023 = Gestion.query.filter_by(anio=2023).order_by(Gestion.id).all()
            print(f"- Total gestiones 2023 en DB: {len(todas_gestiones_2023)}")
            
            for gestion in todas_gestiones_2023:
                print(f"  * ID {gestion.id}: Año {gestion.anio} Trimestre {gestion.periodo}")
            
            print("\nGESTIONES 2023 CON NOTAS LISTAS!")
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    crear_gestiones_2023_con_notas()