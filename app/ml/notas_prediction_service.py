"""
Servicio de integración para predecir notas estimadas
"""

from app.ml.ml_service import ml_service
from app.models.NotaEstimada_Model import NotaEstimada
from app.models.NotaFinal_Model import NotaFinal
from app.models.Estudiante_Model import Estudiante
from app import db
import logging

logger = logging.getLogger(__name__)

class NotasPredictionService:
    """Servicio para predecir y actualizar notas estimadas automáticamente"""
    
    @staticmethod
    def predict_and_update_nota_estimada(nota_final):
        """
        Predice y actualiza la nota estimada basada en la nota final
        
        Args:
            nota_final: Instancia de NotaFinal que se acaba de crear/actualizar
        
        Returns:
            NotaEstimada actualizada o None si hubo error
        """
        try:
            # Obtener información del estudiante
            estudiante = Estudiante.query.filter_by(ci=nota_final.estudiante_ci).first()
            
            if not estudiante:
                logger.error(f"No se encontró estudiante con CI: {nota_final.estudiante_ci}")
                return None
            
            # Preparar datos para la predicción
            student_data = {
                'edad': estudiante.calcular_edad() if hasattr(estudiante, 'calcular_edad') else 16,
                'nota_actual': nota_final.valor
            }
            
            # Realizar predicción con el modelo ML
            result = ml_service.predict_performance(student_data)
            
            if not result.get('success', False):
                logger.error(f"Error en predicción de ML: {result.get('error')}")
                return None
            
            # Obtener el valor predictivo
            predicted_score = result.get('predicted_score', 0)
            category = result.get('performance_category', 'No clasificado')
            recommendations = result.get('recommendations', [])
            
            # Buscar si ya existe una nota estimada para este estudiante, materia y gestión
            nota_estimada = NotaEstimada.query.filter_by(
                estudiante_ci=nota_final.estudiante_ci,
                materia_id=nota_final.materia_id,
                gestion_id=nota_final.gestion_id
            ).first()
            
            razon = f"Predicción ML ({category}): " + ", ".join(recommendations[:2])
            
            if nota_estimada:
                # Actualizar nota existente
                nota_estimada.valor_estimado = predicted_score
                nota_estimada.razon_estimacion = razon
            else:
                # Crear nueva nota estimada
                nota_estimada = NotaEstimada(
                    valor_estimado=predicted_score,
                    razon_estimacion=razon,
                    estudiante_ci=nota_final.estudiante_ci,
                    materia_id=nota_final.materia_id,
                    gestion_id=nota_final.gestion_id
                )
                db.session.add(nota_estimada)
            
            # Guardar cambios
            db.session.commit()
            logger.info(f"Nota estimada actualizada para estudiante {nota_final.estudiante_ci}, " +
                       f"materia {nota_final.materia_id}, valor: {predicted_score}")
            
            return nota_estimada
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al actualizar nota estimada: {str(e)}")
            return None
    def predict_student_grade(self, estudiante_ci, materia_id, gestion_id):
        """
        Predice la nota estimada para un estudiante específico
        
        Args:
            estudiante_ci: CI del estudiante
            materia_id: ID de la materia
            gestion_id: ID de la gestión
            
        Returns:
            Dict con nota_estimada y razon
        """
        try:
            from ..ml.ml_service_simple import ml_service_simple
            
            # Obtener información del estudiante
            estudiante = Estudiante.query.filter_by(ci=estudiante_ci).first()
            
            if not estudiante:
                return None
                
            # Obtener nota final actual
            nota_final = NotaFinal.query.filter_by(
                estudiante_ci=estudiante_ci,
                materia_id=materia_id,
                gestion_id=gestion_id
            ).first()
            
            nota_actual = nota_final.valor if nota_final else 0
            
            # Preparar datos para la predicción
            student_data = {
                'edad': estudiante.calcular_edad() if hasattr(estudiante, 'calcular_edad') else 16,
                'nota_actual': nota_actual
            }
            
            # Realizar predicción con el modelo ML simplificado
            result = ml_service_simple.predict_performance(student_data)
            
            if result.get('success', False):
                predicted_score = result.get('predicted_score', nota_actual)
                category = result.get('performance_category', 'No clasificado')
                recommendations = result.get('recommendations', [])
                
                return {
                    'nota_estimada': predicted_score,
                    'razon': f"Predicción ML ({category}): " + ", ".join(recommendations[:2]) if recommendations else f"Predicción ML ({category})"
                }
            else:
                # Si falla ML, usar nota actual + pequeño ajuste
                return {
                    'nota_estimada': min(100, nota_actual + 5),
                    'razon': 'Predicción basada en rendimiento actual (ML no disponible)'
                }
                
        except Exception as e:
            logger.error(f"Error en predict_student_grade: {str(e)}")
            # Retornar predicción básica como fallback
            return {
                'nota_estimada': 75.0,
                'razon': 'Predicción estimada por defecto'
            }

notas_prediction_service = NotasPredictionService()
