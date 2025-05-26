from ..models.Gestion_Model import Gestion
from ..models.NotaFinal_Model import NotaFinal
from ..models.NotaEstimada_Model import NotaEstimada
from ..models.Estudiante_Model import Estudiante
from ..models.Materia_Model import Materia
from ..schemas.Gestion_schema import GestionSchema
from ..models.MateriaCurso_Model import MateriaCurso
from ..models.Inscripcion_Model import Inscripcion
from flask import request
from app import db
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from ..api_model.Gestion import ns, gestion_model_request, gestion_model_response

gestion_schema = GestionSchema()
gestiones_schema = GestionSchema(many=True)

@ns.route('/')
class GestionList(Resource):
    @ns.marshal_list_with(gestion_model_response)
    @jwt_required()
    def get(self):
        """Lista todas las gestiones"""
        gestiones = Gestion.query.all()
        return gestiones_schema.dump(gestiones)

    @ns.expect(gestion_model_request)
    @ns.marshal_with(gestion_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva gestión"""
        data = request.json
        nueva_gestion = gestion_schema.load(data)
        try:
            db.session.add(nueva_gestion)
            db.session.commit()
            return gestion_schema.dump(nueva_gestion), 201
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la gestión: {str(e)}")

@ns.route('/<int:id>')
@ns.param('id', 'ID de la gestión')
class GestionResource(Resource):
    @ns.marshal_with(gestion_model_response)
    @jwt_required()
    def get(self, id):
        """Obtiene una gestión por ID"""
        return Gestion.query.get_or_404(id)

    @ns.expect(gestion_model_request)
    @ns.marshal_with(gestion_model_response)
    @jwt_required()
    def put(self, id):
        """Actualiza una gestión por ID"""
        gestion = Gestion.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            if hasattr(gestion, key):
                setattr(gestion, key, value)

        try:
            db.session.commit()
            return gestion_schema.dump(gestion)
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al actualizar la gestión: {str(e)}")

    @jwt_required()
    def delete(self, id):
        """Elimina una gestión por ID"""
        gestion = Gestion.query.get_or_404(id)
        try:
            db.session.delete(gestion)
            db.session.commit()
            return {"message": "Gestión eliminada correctamente"}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al eliminar la gestión: {str(e)}")


@ns.route('/with-notas')
class GestionWithNotas(Resource):
    @ns.expect(gestion_model_request)
    @ns.marshal_with(gestion_model_response, code=201)
    @jwt_required()
    def post(self):
        """Crea una nueva gestión y genera notas para cada estudiante en base a su curso y materias"""
        data = request.json
        nueva_gestion = gestion_schema.load(data)

        try:
            db.session.add(nueva_gestion)
            db.session.commit()  # Para obtener nueva_gestion.id

            estudiantes = Estudiante.query.all()

            for est in estudiantes:
                # Obtener la inscripción activa del estudiante (última o principal)
                inscripcion = Inscripcion.query.filter_by(estudiante_ci=est.ci).order_by(Inscripcion.fecha.desc()).first()
                if not inscripcion:
                    continue  # Saltar si no tiene curso

                curso = inscripcion.curso
                if not curso:
                    continue  # Saltar si no tiene curso asignado

                # Obtener materias asociadas al curso
                materias_curso = MateriaCurso.query.filter_by(curso_id=curso.id).all()

                for mc in materias_curso:
                    materia = mc.materia
                    if not materia:
                        continue

                    nota_final = NotaFinal(
                        valor=0.0,
                        estudiante_ci=est.ci,
                        gestion_id=nueva_gestion.id,
                        materia_id=materia.id
                    )
                    db.session.add(nota_final)

                    nota_estimada = NotaEstimada(
                        valor_estimado=0.0,
                        razon_estimacion="Generada automáticamente con la gestión",
                        estudiante_ci=est.ci,
                        gestion_id=nueva_gestion.id,
                        materia_id=materia.id
                    )
                    db.session.add(nota_estimada)

            db.session.commit()
            return gestion_schema.dump(nueva_gestion), 201

        except Exception as e:
            db.session.rollback()
            ns.abort(500, f"Error al crear la gestión con notas: {str(e)}")