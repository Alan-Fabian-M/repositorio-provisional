from ..models.Evaluacion_Model import Evaluacion
from ..models.EvaluacionIntegral_Model import EvaluacionIntegral
from ..models.TipoEvaluacion_Model import TipoEvaluacion
from ..models.Gestion_Model import Gestion
from ..models.Materia_Model import Materia
from ..models.NotaEstimada_Model import NotaEstimada
from ..models.NotaFinal_Model import NotaFinal
from ..models.MateriaCurso_Model import MateriaCurso
from ..models.Inscripcion_Model import Inscripcion

from ..schemas.Evaluacion_schema import EvaluacionSchema
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.Evaluacion import ns, evaluacion_model_request, evaluacion_model_response
from sqlalchemy import func

evaluacion_schema = EvaluacionSchema()
evaluaciones_schema = EvaluacionSchema(many=True)

@ns.route('/')
class EvaluacionList(Resource):
    @ns.marshal_list_with(evaluacion_model_response)
    @jwt_required()
    def get(self):
        """Lista todas las evaluaciones"""
        items = Evaluacion.query.all()
        return evaluaciones_schema.dump(items)    @ns.expect(evaluacion_model_request)
    @ns.marshal_with(evaluacion_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva evaluación y actualiza la nota final"""
        data = request.json
        nueva_evaluacion = evaluacion_schema.load(data)

        try:
            # Guardar evaluación
            db.session.add(nueva_evaluacion)
            db.session.commit()

            # === Actualizar Nota Final del estudiante para esa materia y gestión ===
            estudiante_ci = data["estudiante_ci"]
            gestion_id = data["gestion_id"]
            materia_id = data["materia_id"]

            # Obtener notas individuales
            ser_nota = NotaFinalDe(estudiante_ci, gestion_id, materia_id, "ser")
            hacer_nota = NotaFinalDe(estudiante_ci, gestion_id, materia_id, "hacer")
            saber_nota = NotaFinalDe(estudiante_ci, gestion_id, materia_id, "saber")
            decidir_nota = NotaFinalDe(estudiante_ci, gestion_id, materia_id, "decidir")

            def extraer_nota(valor):
                return valor["Nota"] if isinstance(valor, dict) and "Nota" in valor else 0

            # Calcular nota final integral (suma directa, sin dividir)
            # Cada dimensión ya tiene su peso correcto: ser=15, decidir=15, hacer=35, saber=35 = 100 total
            nota_final_valor = round((
                extraer_nota(ser_nota) +
                extraer_nota(hacer_nota) +
                extraer_nota(saber_nota) +
                extraer_nota(decidir_nota)
            ), 2)

            # Buscar o crear NotaFinal
            nota_final = NotaFinal.query.filter_by(
                estudiante_ci=estudiante_ci,
                gestion_id=gestion_id,
                materia_id=materia_id
            ).first()

            if not nota_final:
                nota_final = NotaFinal(
                    estudiante_ci=estudiante_ci,
                    gestion_id=gestion_id,
                    materia_id=materia_id,
                    valor=nota_final_valor
                )
                db.session.add(nota_final)
            else:
                nota_final.valor = nota_final_valor

            db.session.commit()

            return evaluacion_schema.dump(nueva_evaluacion), 201

        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la evaluación: {str(e)}")

@ns.route('/boletin/<int:estudiante_ci>')
class BoletinEstudiante(Resource):
    @jwt_required()
    def get(self, estudiante_ci):
        """Devuelve el boletín del estudiante con promedio por materia"""
        notas = NotaFinal.query.filter_by(estudiante_ci=estudiante_ci).all()

        if not notas:
            return {"message": "No hay notas finales registradas para este estudiante"}, 404

        boletin = {}  # Gestion -> lista de materias con nota
        resumen_materias = {}  # Materia ID -> lista de notas

        for nota in notas:
            gestion = Gestion.query.get(nota.gestion_id)
            materia = Materia.query.get(nota.materia_id)

            if not gestion or not materia:
                continue

            clave_gestion = f"{gestion.anio} - {gestion.periodo}"

            # Agregar a boletín por gestión
            if clave_gestion not in boletin:
                boletin[clave_gestion] = []

            boletin[clave_gestion].append({
                "materia_id": materia.id,
                "materia_nombre": materia.nombre,
                "nota_final": nota.valor
            })

            # Agregar al resumen por materia
            if materia.id not in resumen_materias:
                resumen_materias[materia.id] = {
                    "materia_nombre": materia.nombre,
                    "notas": []
                }

            resumen_materias[materia.id]["notas"].append(nota.valor)

        # Calcular promedio general por materia
        resumen_final = []
        for materia_id, data in resumen_materias.items():
            notas = data["notas"]
            promedio = sum(notas) / len(notas) if notas else 0

            resumen_final.append({
                "materia_id": materia_id,
                "materia_nombre": data["materia_nombre"],
                "promedio_final": round(promedio, 2)
            })

        return {
            "estudiante_ci": estudiante_ci,
            "boletin": boletin,
            "promedio_por_materia": resumen_final
        }, 200


@ns.route('/paso_notas/curso/<int:curso_id>/gestion/<int:gestion_id>')
class PasarNotasDeEvaluacionANotaFinal(Resource):
    @jwt_required()
    def get(self, curso_id, gestion_id):
        """Genera o actualiza las notas finales de los estudiantes en un curso dado y gestión"""

        # Obtener todas las materias asignadas a este curso
        materias_curso = MateriaCurso.query.filter_by(curso_id=curso_id).all()
        if not materias_curso:
            return {"mensaje": "No hay materias asignadas al curso"}, 404

        materia_ids = [mc.materia_id for mc in materias_curso]

        # Obtener todos los estudiantes inscritos en el curso
        inscripciones = Inscripcion.query.filter_by(curso_id=curso_id).all()
        if not inscripciones:
            return {"mensaje": "No hay estudiantes inscritos en este curso"}, 404

        total_procesados = 0
        errores = []

        for inscripcion in inscripciones:
            estudiante_ci = inscripcion.estudiante_ci

            for materia_id in materia_ids:
                # Obtener todas las evaluaciones del estudiante en esa materia y gestión
                evaluaciones = Evaluacion.query.filter_by(
                    estudiante_ci=estudiante_ci,
                    materia_id=materia_id,
                    gestion_id=gestion_id
                ).all()

                if not evaluaciones:
                    continue  # No hay evaluaciones, saltamos

                suma = sum(eva.nota for eva in evaluaciones)
                promedio = round(suma / len(evaluaciones), 2)

                # Verificamos si ya existe una nota final para este estudiante/materia/gestión
                nota_final = NotaFinal.query.filter_by(
                    estudiante_ci=estudiante_ci,
                    materia_id=materia_id,
                    gestion_id=gestion_id
                ).first()

                try:
                    if nota_final:
                        # Actualizar
                        nota_final.valor = promedio
                    else:
                        # Crear
                        nota_final = NotaFinal(
                            estudiante_ci=estudiante_ci,
                            materia_id=materia_id,
                            gestion_id=gestion_id,
                            valor=promedio
                        )   
                        db.session.add(nota_final)

                    total_procesados += 1

                except Exception as e:
                    errores.append({
                        "estudiante_ci": estudiante_ci,
                        "materia_id": materia_id,
                        "error": str(e)
                    })

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"mensaje": "Error al guardar los cambios", "error": str(e)}, 500

        return {
            "mensaje": f"Notas finales procesadas correctamente: {total_procesados}",
            "errores": errores
        }, 200




# @ns.route('/boletin_resumen/<int:estudiante_ci>')
# class BoletinResumenFinal(Resource):
#     @jwt_required()
#     def get(self, estudiante_ci):
#         """Boletín resumen final por materia con nota estimada incluida"""

#         notas_finales = NotaFinal.query.filter_by(estudiante_ci=estudiante_ci).all()
#         if not notas_finales:
#             return {"message": "No hay notas finales registradas para este estudiante"}, 404

#         resumen_materias = {}

#         # 1. Agrupar y promediar notas finales por materia
#         for nota in notas_finales:
#             materia = Materia.query.get(nota.materia_id)
#             if not materia:
#                 continue

#             if materia.id not in resumen_materias:
#                 resumen_materias[materia.id] = {
#                     "materia_nombre": materia.nombre,
#                     "notas": []
#                 }

#             resumen_materias[materia.id]["notas"].append(nota.valor)

#         resultado_final = []

#         for materia_id, data in resumen_materias.items():
#             promedio = sum(data["notas"]) / len(data["notas"]) if data["notas"] else 0
#             promedio = round(promedio, 2)

#             # 2. Buscar la nota estimada más reciente (puedes cambiar la lógica)
#             nota_estimada = NotaEstimada.query.filter_by(
#                 estudiante_ci=estudiante_ci,
#                 materia_id=materia_id
#             ).order_by(NotaEstimada.gestion_id.desc()).first()

#             resultado_final.append({
#                 "materia_id": materia_id,
#                 "materia_nombre": data["materia_nombre"],
#                 "promedio_final": promedio,
#                 "nota_estimada": nota_estimada.valor_estimado if nota_estimada else None,
#                 "razon_estimacion": nota_estimada.razon_estimacion if nota_estimada else None
#             })

#         return {
#             "estudiante_ci": estudiante_ci,
#             "resumen_final_materias": resultado_final
#         }, 200

@ns.route('/asistencia/')
class AsistenciaPost(Resource):
    @ns.expect(evaluacion_model_request)
    # @ns.marshal_with(evaluacion_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva evaluación de asistencia diaria, actualiza asistencia final y recalcula nota final"""
        data = request.json
        data['tipo_evaluacion_id'] = 1  # ID fijo para Asistencia-Diaria
        nueva_evaluacion = evaluacion_schema.load(data)

        try:
            # Guardar la asistencia diaria
            db.session.add(nueva_evaluacion)
            db.session.commit()

            # Actualizar o crear la evaluación de tipo Asistencia-Final (ID fijo = 2)
            tipoAsistenciaFinal = Evaluacion.query.filter_by(
                tipo_evaluacion_id=2,  # ID fijo para Asistencia-Final
                estudiante_ci=data["estudiante_ci"],
                materia_id=data["materia_id"],
                gestion_id=data["gestion_id"]
            ).first()

            resultado_asistencia = AsistenciaFinal(data["estudiante_ci"], data["gestion_id"], data["materia_id"])
            nota_asistencia_final = resultado_asistencia.get("asistenciaFinal", 0)

            if not tipoAsistenciaFinal:
                tipoAsistenciaFinal = Evaluacion(
                    estudiante_ci=data["estudiante_ci"],
                    materia_id=data["materia_id"],
                    gestion_id=data["gestion_id"],
                    tipo_evaluacion_id=2,  # ID fijo para Asistencia-Final
                    nota=nota_asistencia_final
                )
                db.session.add(tipoAsistenciaFinal)
            else:
                tipoAsistenciaFinal.nota = nota_asistencia_final
                db.session.add(tipoAsistenciaFinal)

            db.session.commit()            # === Recalcular Nota Final del estudiante para esa materia y gestión ===
            estudiante_ci = data["estudiante_ci"]
            gestion_id = data["gestion_id"]
            materia_id = data["materia_id"]

            ser_nota = NotaFinalDe(estudiante_ci, gestion_id, materia_id, "ser")
            hacer_nota = NotaFinalDe(estudiante_ci, gestion_id, materia_id, "hacer")
            saber_nota = NotaFinalDe(estudiante_ci, gestion_id, materia_id, "saber")
            decidir_nota = NotaFinalDe(estudiante_ci, gestion_id, materia_id, "decidir")

            def extraer_nota(valor):
                return valor["Nota"] if isinstance(valor, dict) and "Nota" in valor else 0

            # Calcular nota final integral (suma directa, sin dividir)
            # Cada dimensión ya tiene su peso correcto: ser=15, decidir=15, hacer=35, saber=35 = 100 total
            nota_final_valor = round((
                extraer_nota(ser_nota) +
                extraer_nota(hacer_nota) +
                extraer_nota(saber_nota) +
                extraer_nota(decidir_nota)
            ), 2)

            # Buscar o crear NotaFinal
            nota_final = NotaFinal.query.filter_by(
                estudiante_ci=estudiante_ci,
                gestion_id=gestion_id,
                materia_id=materia_id
            ).first()

            if not nota_final:
                nota_final = NotaFinal(
                    estudiante_ci=estudiante_ci,
                    gestion_id=gestion_id,
                    materia_id=materia_id,
                    valor=nota_final_valor
                )
                db.session.add(nota_final)
            else:
                nota_final.valor = nota_final_valor

            db.session.commit()

            return evaluacion_schema.dump(nueva_evaluacion), 201

        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la evaluación de asistencia: {str(e)}")
    

@ns.route('/asistencia/estudiante/<int:estudiante_ci>/gestion/<int:gestion_id>/materia/<int:materia_id>')
@ns.doc(params={
    'estudiante_ci': 'CI del estudiante',
    'gestion_id': 'ID de la gestión',
    'materia_id': 'ID de la materia'
})
class AsistenciaFinal(Resource):
    
    @jwt_required()
    def get(self, estudiante_ci, gestion_id, materia_id):
        return AsistenciaFinal(estudiante_ci, gestion_id, materia_id)
    
def AsistenciaFinal(estudiante_ci, gestion_id, materia_id):
    evaluaciones = Evaluacion.query.filter_by(
        estudiante_ci=estudiante_ci,
        materia_id=materia_id,
        gestion_id=gestion_id,
        tipo_evaluacion_id=1  # ID fijo para Asistencia-Diaria
    ).all()

    if not evaluaciones:
        return {"mensaje": "No se encontraron evaluaciones"}, 404

    suma = sum(eva.nota for eva in evaluaciones)
    promedio = suma / len(evaluaciones)

    return {"asistenciaFinal": promedio}




    
# @ns.route('/ser-final/estudiante/<int:estudiante_ci>/gestion/<int:gestion_id>/materia/<int:materia_id>')
# @ns.doc(params={
#     'estudiante_ci': 'CI del estudiante',
#     'gestion_id': 'ID de la gestión',
#     'materia_id': 'ID de la materia'
# })
# class EvaluacionFinalSer(Resource):

#     @jwt_required()
#     def get(self, estudiante_ci, gestion_id, materia_id):
#         return NotaFinalDe(estudiante_ci, gestion_id, materia_id, "ser")
    
# @ns.route('/hacer-final/estudiante/<int:estudiante_ci>/gestion/<int:gestion_id>/materia/<int:materia_id>')
# @ns.doc(params={
#     'estudiante_ci': 'CI del estudiante',
#     'gestion_id': 'ID de la gestión',
#     'materia_id': 'ID de la materia'
# })
# class EvaluacionFinalHacer(Resource):

#     @jwt_required()
#     def get(self, estudiante_ci, gestion_id, materia_id):
#         return NotaFinalDe(estudiante_ci, gestion_id, materia_id, "hacer")
    
# @ns.route('/decidir-final/estudiante/<int:estudiante_ci>/gestion/<int:gestion_id>/materia/<int:materia_id>')
# @ns.doc(params={
#     'estudiante_ci': 'CI del estudiante',
#     'gestion_id': 'ID de la gestión',
#     'materia_id': 'ID de la materia'
# })
# class EvaluacionFinalDecidir(Resource):

#     @jwt_required()
#     def get(self, estudiante_ci, gestion_id, materia_id):
#         return NotaFinalDe(estudiante_ci, gestion_id, materia_id, "decidir")
    
# @ns.route('/saber-final/estudiante/<int:estudiante_ci>/gestion/<int:gestion_id>/materia/<int:materia_id>')
# @ns.doc(params={
#     'estudiante_ci': 'CI del estudiante',
#     'gestion_id': 'ID de la gestión',
#     'materia_id': 'ID de la materia'
# })
# class EvaluacionFinalSaber(Resource):

#     @jwt_required()
#     def get(self, estudiante_ci, gestion_id, materia_id):
#         return NotaFinalDe(estudiante_ci, gestion_id, materia_id, "saber")





def NotaFinalDe(estudiante_ci, gestion_id, materia_id, tipoDeEvaluacionIntegral):
    # Buscar la EvaluacionIntegral que se llama "ser"
    evaluacion_integral = EvaluacionIntegral.query.filter(func.lower(EvaluacionIntegral.nombre) == tipoDeEvaluacionIntegral).first()
    if not evaluacion_integral:
        return {"mensaje": "evaluacion integral no encontrada"}, 404

    # Obtener los tipos de evaluación relacionados al SER
    tipos_ser = TipoEvaluacion.query.filter_by(evaluacion_integral_id=evaluacion_integral.id).all()
    tipo_ids = [tipo.id for tipo in tipos_ser]

    if not tipo_ids:
        return {"Nota": 0}, 404

    # Buscar todas las evaluaciones del estudiante en esa materia y gestión que correspondan al SER
    evaluaciones = Evaluacion.query.filter(
        Evaluacion.estudiante_ci == estudiante_ci,
        Evaluacion.materia_id == materia_id,
        Evaluacion.gestion_id == gestion_id,
        Evaluacion.tipo_evaluacion_id.in_(tipo_ids)
    ).all()

    if not evaluaciones:
        return {"mensaje": "No se encontraron evaluaciones de la evaluacion integral"}, 404

    # Calcular la suma de notas
    suma = sum(eva.nota for eva in evaluaciones)
    promedio = suma / len(evaluaciones)

    return {"Nota": promedio}

@ns.route('/estudiante/<int:estudiante_ci>')
@ns.param('estudiante_ci', 'CI del estudiante')
class EvaluacionesPorEstudiante(Resource):
    @ns.marshal_list_with(evaluacion_model_response)
    @jwt_required()
    def get(self, estudiante_ci):
        """Buscar evaluaciones por CI del estudiante"""
        evaluaciones = Evaluacion.query.filter_by(estudiante_ci=estudiante_ci).all()
        if not evaluaciones:
            ns.abort(404, f"No se encontraron evaluaciones para el estudiante con CI {estudiante_ci}")
        return evaluaciones_schema.dump(evaluaciones)


# @ns.route('/AsistenciaFinal')
# class EvaluacionResource(Resource):
#     @ns.marshal_with(evaluacion_model_response)
#     @jwt_required()
#     def get(self, id):
#         """Obtener una evaluación por ID"""
#         return Evaluacion.query.get_or_404(id)

#     @ns.expect(evaluacion_model_request)
#     @ns.marshal_with(evaluacion_model_response)
#     @jwt_required()
#     def put(self, id):
#         """Actualizar una evaluación por ID"""
#         evaluacion = Evaluacion.query.get_or_404(id)
#         data = request.json

#         for key, value in data.items():
#             if hasattr(evaluacion, key):
#                 setattr(evaluacion, key, value)

#         try:
#             db.session.commit()
#             return evaluacion_schema.dump(evaluacion)
#         except Exception as e:
#             db.session.rollback()
#             ns.abort(500, f"Error al actualizar: {str(e)}")


@ns.route('/<int:id>')
@ns.param('id', 'ID de la evaluación')
class EvaluacionResource(Resource):
    @ns.marshal_with(evaluacion_model_response)
    @jwt_required()
    def get(self, id):
        """Obtener una evaluación por ID"""
        return Evaluacion.query.get_or_404(id)

    @ns.expect(evaluacion_model_request)
    @ns.marshal_with(evaluacion_model_response)
    @jwt_required()
    def put(self, id):
        """Actualizar una evaluación por ID"""
        evaluacion = Evaluacion.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(evaluacion, key):
                setattr(evaluacion, key, value)

        try:
            db.session.commit()
            return evaluacion_schema.dump(evaluacion)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Eliminar una evaluación por ID"""
        evaluacion = Evaluacion.query.get_or_404(id)
        try:
            db.session.delete(evaluacion)
            db.session.commit()
            return {"message": "Evaluación eliminada correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar: {str(e)}")


@ns.route('/estudiante/<int:estudiante_ci>')
@ns.param('estudiante_ci', 'CI del estudiante')
class EvaluacionesPorEstudiante(Resource):
    @ns.marshal_list_with(evaluacion_model_response)
    @jwt_required()
    def get(self, estudiante_ci):
        """Buscar evaluaciones por CI del estudiante"""
        evaluaciones = Evaluacion.query.filter_by(estudiante_ci=estudiante_ci).all()
        if not evaluaciones:
            ns.abort(404, f"No se encontraron evaluaciones para el estudiante con CI {estudiante_ci}")
        return evaluaciones_schema.dump(evaluaciones)


@ns.route('/estudiante/<int:estudiante_ci>/NotaAsistenciaFinal')
class EvaluacionesPorEstudiante(Resource):
    @ns.marshal_list_with(evaluacion_model_response)
    @jwt_required()
    def get(self, estudiante_ci):
        """Buscar evaluaciones por CI del estudiante"""
        evaluaciones = Evaluacion.query.filter_by(estudiante_ci=estudiante_ci).all()
        if not evaluaciones:
            ns.abort(404, f"No se encontraron evaluaciones para el estudiante con CI {estudiante_ci}")
        return evaluaciones_schema.dump(evaluaciones)
    


@ns.route('/boletin/gestion/<int:gestion_id>/materia/<int:materia_id>/curso/<int:curso_id>')
class BoletinPorMateria(Resource):
    @jwt_required()
    def get(self, gestion_id, materia_id, curso_id):
        """Retorna un boletín por materia, gestión y curso con notas por estudiante"""
        
        # Verificar que la materia esté asignada al curso
        mc = MateriaCurso.query.filter_by(
            materia_id=materia_id,
            curso_id=curso_id
        ).first()
        if not mc:
            return {'mensaje': 'La materia no pertenece a ese curso'}, 404

        # Obtener inscripciones al curso
        inscripciones = Inscripcion.query.filter_by(curso_id=curso_id).all()
        estudiantes = [ins.estudiante for ins in inscripciones]

        resultado = []

        for estudiante in estudiantes:
            ser = getSer(estudiante.ci, gestion_id, materia_id)
            hacer = getHacer(estudiante.ci, gestion_id, materia_id)
            saber = getSaber(estudiante.ci, gestion_id, materia_id)
            decidir = getDecidir(estudiante.ci, gestion_id, materia_id)            # Si alguna nota vino como error (tupla), la manejamos
            def nota_valida(valor):
                if isinstance(valor, dict) and "Nota" in valor:
                    return valor["Nota"]
                return 0  # Por defecto si hubo error

            ser_nota = nota_valida(ser)
            hacer_nota = nota_valida(hacer)
            saber_nota = nota_valida(saber)
            decidir_nota = nota_valida(decidir)

            # Calcular nota final integral (suma directa, sin dividir)
            # Cada dimensión ya tiene su peso correcto: ser=15, decidir=15, hacer=35, saber=35 = 100 total
            nota_final_valor = round((ser_nota + hacer_nota + saber_nota + decidir_nota), 2)

            resultado.append({
                "ci": estudiante.ci,
                "nombreCompleto": estudiante.nombreCompleto,
                "ser": ser_nota,
                "hacer": hacer_nota,
                "saber": saber_nota,
                "decidir": decidir_nota,
                "nota_final": nota_final_valor
            })

        return resultado, 200


def getSer(estudiante_ci, gestion_id, materia_id):
    return NotaFinalDe(estudiante_ci, gestion_id, materia_id, "ser")

def getHacer(estudiante_ci, gestion_id, materia_id):
    return NotaFinalDe(estudiante_ci, gestion_id, materia_id, "hacer")

def getDecidir(estudiante_ci, gestion_id, materia_id):
    return NotaFinalDe(estudiante_ci, gestion_id, materia_id, "decidir")

def getSaber(estudiante_ci, gestion_id, materia_id):
    return NotaFinalDe(estudiante_ci, gestion_id, materia_id, "saber")

def NotaFinalDe(estudiante_ci, gestion_id, materia_id, tipoDeEvaluacionIntegral):
    # Buscar la EvaluacionIntegral que se llama "ser"
    evaluacion_integral = EvaluacionIntegral.query.filter(func.lower(EvaluacionIntegral.nombre) == tipoDeEvaluacionIntegral).first()
    if not evaluacion_integral:
        return {"mensaje": "evaluacion integral no encontrada"}, 404

    # Obtener los tipos de evaluación relacionados al SER
    tipos_ser = TipoEvaluacion.query.filter_by(evaluacion_integral_id=evaluacion_integral.id).all()
    tipo_ids = [tipo.id for tipo in tipos_ser]

    if not tipo_ids:
        return {"Nota": 0}, 404

    # Buscar todas las evaluaciones del estudiante en esa materia y gestión que correspondan al SER
    evaluaciones = Evaluacion.query.filter(
        Evaluacion.estudiante_ci == estudiante_ci,
        Evaluacion.materia_id == materia_id,
        Evaluacion.gestion_id == gestion_id,
        Evaluacion.tipo_evaluacion_id.in_(tipo_ids)
    ).all()

    if not evaluaciones:
        return {"mensaje": "No se encontraron evaluaciones de la evaluacion integral"}, 404

    # Calcular la suma de notas
    suma = sum(eva.nota for eva in evaluaciones)
    promedio = suma / len(evaluaciones)

    return {"Nota": promedio}


