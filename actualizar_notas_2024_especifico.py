"""
Script para actualizar específicamente las notas estimadas de gestiones 2024 que están en 0.0
"""

import requests
import json
from app import create_app, db
from app.models.NotaEstimada_Model import NotaEstimada
from app.models.NotaFinal_Model import NotaFinal
from app.models.Gestion_Model import Gestion
from app.ml.notas_prediction_service import notas_prediction_service
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def actualizar_notas_2024():
    """
    Actualiza todas las notas estimadas de 2024 que están en 0.0
    """
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Obtener todas las gestiones de 2024
            gestiones_2024 = Gestion.query.filter(Gestion.anio == 2024).all()
            
            if not gestiones_2024:
                logger.error("No se encontraron gestiones de 2024")
                return
            
            gestion_ids_2024 = [g.id for g in gestiones_2024]
            logger.info(f"Encontradas {len(gestiones_2024)} gestiones de 2024: {gestion_ids_2024}")
            
            # 2. Obtener todas las notas estimadas de 2024 que están en 0.0
            notas_estimadas_cero = NotaEstimada.query.filter(
                NotaEstimada.gestion_id.in_(gestion_ids_2024),
                NotaEstimada.valor_estimado == 0.0
            ).all()
            
            logger.info(f"Encontradas {len(notas_estimadas_cero)} notas estimadas en 0.0 para gestiones 2024")
            
            # 3. Procesar cada nota estimada
            actualizadas = 0
            errores = 0
            
            for i, nota_estimada in enumerate(notas_estimadas_cero, 1):
                try:
                    logger.info(f"Procesando {i}/{len(notas_estimadas_cero)}: "
                              f"Estudiante {nota_estimada.estudiante_ci}, "
                              f"Materia {nota_estimada.materia_id}, "
                              f"Gestión {nota_estimada.gestion_id}")
                    
                    # Buscar la nota final correspondiente
                    nota_final = NotaFinal.query.filter_by(
                        estudiante_ci=nota_estimada.estudiante_ci,
                        materia_id=nota_estimada.materia_id,
                        gestion_id=nota_estimada.gestion_id
                    ).first()
                    
                    if not nota_final:
                        logger.warning(f"No se encontró nota final para estudiante {nota_estimada.estudiante_ci}")
                        continue
                    
                    # Usar el servicio de predicción ML
                    resultado = notas_prediction_service.predict_student_grade(
                        nota_estimada.estudiante_ci,
                        nota_estimada.materia_id,
                        nota_estimada.gestion_id
                    )
                    
                    if resultado:
                        # Actualizar la nota estimada
                        nota_estimada.valor_estimado = resultado['nota_estimada']
                        nota_estimada.razon_estimacion = resultado['razon']
                        
                        db.session.commit()
                        actualizadas += 1
                        
                        logger.info(f"✓ Actualizada: {resultado['nota_estimada']:.2f} - {resultado['razon']}")
                    else:
                        logger.warning(f"No se pudo generar predicción para estudiante {nota_estimada.estudiante_ci}")
                        errores += 1
                    
                    # Mostrar progreso cada 100 registros
                    if i % 100 == 0:
                        logger.info(f"Progreso: {i}/{len(notas_estimadas_cero)} - "
                                  f"Actualizadas: {actualizadas}, Errores: {errores}")
                
                except Exception as e:
                    logger.error(f"Error procesando nota estimada ID {nota_estimada.id}: {str(e)}")
                    errores += 1
                    db.session.rollback()
            
            # Resumen final
            logger.info(f"\n=== RESUMEN FINAL ===")
            logger.info(f"Total procesadas: {len(notas_estimadas_cero)}")
            logger.info(f"Actualizadas exitosamente: {actualizadas}")
            logger.info(f"Errores: {errores}")
            logger.info(f"===================")
            
        except Exception as e:
            logger.error(f"Error general en el proceso: {str(e)}")
            db.session.rollback()

def verificar_estado_antes_y_despues():
    """Verifica el estado antes y después de la actualización"""
    app = create_app()
    
    with app.app_context():
        try:
            # Obtener gestiones 2024
            gestiones_2024 = Gestion.query.filter(Gestion.anio == 2024).all()
            gestion_ids_2024 = [g.id for g in gestiones_2024]
            
            # Contar notas estimadas por valor
            total_2024 = NotaEstimada.query.filter(
                NotaEstimada.gestion_id.in_(gestion_ids_2024)
            ).count()
            
            cero_2024 = NotaEstimada.query.filter(
                NotaEstimada.gestion_id.in_(gestion_ids_2024),
                NotaEstimada.valor_estimado == 0.0
            ).count()
            
            con_valor_2024 = total_2024 - cero_2024
            
            print(f"\n=== ESTADO GESTIONES 2024 ===")
            print(f"Total notas estimadas: {total_2024}")
            print(f"Con valor 0.0: {cero_2024}")
            print(f"Con valor > 0.0: {con_valor_2024}")
            print(f"=============================")
            
        except Exception as e:
            logger.error(f"Error verificando estado: {str(e)}")

if __name__ == "__main__":
    print("Verificando estado inicial...")
    verificar_estado_antes_y_despues()
    
    respuesta = input("\n¿Proceder con la actualización de notas 2024? (s/n): ")
    
    if respuesta.lower() in ['s', 'si', 'y', 'yes']:
        print("Iniciando actualización...")
        actualizar_notas_2024()
        
        print("\nVerificando estado final...")
        verificar_estado_antes_y_despues()
    else:
        print("Operación cancelada.")
