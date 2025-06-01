from app import db
from ..models.TipoEvaluacion_Model import TipoEvaluacion
from ..models.EvaluacionIntegral_Model import EvaluacionIntegral

def seed_evaluacion_integral():
    # Check if table is empty
    if EvaluacionIntegral.query.count() == 0:
        evaluaciones_integrales = [
            EvaluacionIntegral(
                id=1,
                nombre="ser",
                maxPuntos=15
            ),
            EvaluacionIntegral(
                id=2,
                nombre="decidir",
                maxPuntos=15
            ),
            EvaluacionIntegral(
                id=3,
                nombre="saber",
                maxPuntos=35
            ),
            EvaluacionIntegral(
                id=4,
                nombre="hacer",
                maxPuntos=35
            )
        ]
        
        try:
            for evaluacion in evaluaciones_integrales:
                db.session.add(evaluacion)
            db.session.commit()
            print("Evaluaciones integrales creadas exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear evaluaciones integrales: {str(e)}")

def seed_tipo_evaluacion():
    # Check if table is empty
    if TipoEvaluacion.query.count() == 0:
        tipos = [
            TipoEvaluacion(
                id=1,
                nombre="Asistencia-Diaria",
                evaluacion_integral_id=1
            ),
            TipoEvaluacion(
                id=2,
                nombre="Asistencia-Final",
                evaluacion_integral_id=1
            )
        ]
        
        try:
            for tipo in tipos:
                db.session.add(tipo)
            db.session.commit()
            print("Tipos de evaluación de asistencia creados exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear tipos de evaluación: {str(e)}")
