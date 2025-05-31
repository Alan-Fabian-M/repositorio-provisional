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
                descripcion="Dimensión del ser",
                puntaje=15
            ),
            EvaluacionIntegral(
                id=2,
                nombre="decidir",
                descripcion="Dimensión del decidir",
                puntaje=15
            ),
            EvaluacionIntegral(
                id=3,
                nombre="saber",
                descripcion="Dimensión del saber",
                puntaje=35
            ),
            EvaluacionIntegral(
                id=4,
                nombre="hacer",
                descripcion="Dimensión del hacer",
                puntaje=35
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
                descripcion="Registro de asistencia diaria"
            ),
            TipoEvaluacion(
                id=2,
                nombre="Asistencia-Final",
                descripcion="Promedio final de asistencia"
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
