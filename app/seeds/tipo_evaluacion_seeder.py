from app import db
from ..models.TipoEvaluacion_Model import TipoEvaluacion
from ..models.EvaluacionIntegral_Model import EvaluacionIntegral
from ..models.Materia_Model import Materia
from ..models.Curso_Model import Curso
from ..models.MateriaCurso_Model import MateriaCurso
from ..models.Estudiante_Model import Estudiante
from ..models.Inscripcion_Model import Inscripcion
from datetime import date
import random

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

def seed_materias():
    # Check if table is empty
    if Materia.query.count() == 0:
        materias = []
        id_counter = 1
        
        # Lista de materias base
        materias_base = [
            {"nombre": "Matemáticas", "descripcion": "Asignatura que desarrolla el pensamiento lógico y las habilidades numéricas", "codigo_base": "MAT"},
            {"nombre": "Ciencias Sociales", "descripcion": "Estudio de la sociedad, historia, geografía y cultura", "codigo_base": "CS"},
            {"nombre": "Ciencias Naturales", "descripcion": "Estudio de la naturaleza, biología y ecosistemas", "codigo_base": "CN"},
            {"nombre": "Inglés", "descripcion": "Aprendizaje del idioma inglés como segunda lengua", "codigo_base": "ING"},
            {"nombre": "Educación Física", "descripcion": "Desarrollo de habilidades físicas, deportes y actividad corporal", "codigo_base": "EF"},
            {"nombre": "Artes Plásticas", "descripcion": "Expresión artística a través de la pintura, dibujo y escultura", "codigo_base": "AP"},
            {"nombre": "Religión", "descripcion": "Formación en valores y enseñanza religiosa", "codigo_base": "REL"},
            {"nombre": "Música", "descripcion": "Educación musical, ritmo, melodía y expresión artística", "codigo_base": "MUS"},
            {"nombre": "Química", "descripcion": "Estudio de la composición, estructura y propiedades de la materia", "codigo_base": "QUI"},
            {"nombre": "Física", "descripcion": "Estudio de las leyes naturales, movimiento, energía y materia", "codigo_base": "FIS"},
            {"nombre": "Lenguaje", "descripcion": "Desarrollo de habilidades de comunicación, lectura y escritura", "codigo_base": "LEN"}
        ]
        
        # Cursos disponibles (1A, 1B, 2A, 2B, 3A, 3B, 4A, 4B, 5A, 5B, 6A, 6B)
        cursos_info = [
            {"numero": "1", "paralelo": "A"}, {"numero": "1", "paralelo": "B"},
            {"numero": "2", "paralelo": "A"}, {"numero": "2", "paralelo": "B"},
            {"numero": "3", "paralelo": "A"}, {"numero": "3", "paralelo": "B"},
            {"numero": "4", "paralelo": "A"}, {"numero": "4", "paralelo": "B"},
            {"numero": "5", "paralelo": "A"}, {"numero": "5", "paralelo": "B"},
            {"numero": "6", "paralelo": "A"}, {"numero": "6", "paralelo": "B"}
        ]
        
        # Crear materias específicas para cada curso
        for curso_info in cursos_info:
            for materia_base in materias_base:
                materia = Materia(
                    id=id_counter,
                    nombre=f"{materia_base['nombre']} {curso_info['numero']}{curso_info['paralelo']}",
                    descripcion=f"{materia_base['descripcion']} - Específica para {curso_info['numero']}° {curso_info['paralelo']}",
                    codigo=f"{materia_base['codigo_base']}{curso_info['numero']}{curso_info['paralelo']}"
                )
                materias.append(materia)
                id_counter += 1
        
        try:
            for materia in materias:
                db.session.add(materia)
            db.session.commit()
            print(f"Materias creadas exitosamente: {len(materias)} materias específicas por curso")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear materias: {str(e)}")

def seed_cursos():
    # Check if table is empty
    if Curso.query.count() == 0:
        cursos = [
            # 1ro de Secundaria
            Curso(
                id=1,
                nombre="1",
                Paralelo="A",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Primer año de educación secundaria, paralelo A, turno mañana"
            ),
            Curso(
                id=2,
                nombre="1",
                Paralelo="B",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Primer año de educación secundaria, paralelo B, turno mañana"
            ),
            # 2do de Secundaria
            Curso(
                id=3,
                nombre="2",
                Paralelo="A",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Segundo año de educación secundaria, paralelo A, turno mañana"
            ),
            Curso(
                id=4,
                nombre="2",
                Paralelo="B",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Segundo año de educación secundaria, paralelo B, turno mañana"
            ),
            # 3ro de Secundaria
            Curso(
                id=5,
                nombre="3",
                Paralelo="A",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Tercer año de educación secundaria, paralelo A, turno mañana"
            ),
            Curso(
                id=6,
                nombre="3",
                Paralelo="B",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Tercer año de educación secundaria, paralelo B, turno mañana"
            ),
            # 4to de Secundaria
            Curso(
                id=7,
                nombre="4",
                Paralelo="A",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Cuarto año de educación secundaria, paralelo A, turno mañana"
            ),
            Curso(
                id=8,
                nombre="4",
                Paralelo="B",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Cuarto año de educación secundaria, paralelo B, turno mañana"
            ),
            # 5to de Secundaria
            Curso(
                id=9,
                nombre="5",
                Paralelo="A",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Quinto año de educación secundaria, paralelo A, turno mañana"
            ),
            Curso(
                id=10,
                nombre="5",
                Paralelo="B",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Quinto año de educación secundaria, paralelo B, turno mañana"
            ),
            # 6to de Secundaria
            Curso(
                id=11,
                nombre="6",
                Paralelo="A",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Sexto año de educación secundaria, paralelo A, turno mañana"
            ),
            Curso(
                id=12,
                nombre="6",
                Paralelo="B",
                Turno="Mañana",
                Nivel="Secundaria",
                descripcion="Sexto año de educación secundaria, paralelo B, turno mañana"
            )
        ]
        
        try:
            for curso in cursos:
                db.session.add(curso)
            db.session.commit()
            print("Cursos creados exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear cursos: {str(e)}")

def seed_materia_curso():
    # Check if table is empty
    if MateriaCurso.query.count() == 0:
        materia_cursos = []
        id_counter = 1
        
        # Obtener el año actual para asignar a cada relación
        anio_actual = 2025
        
        # Ahora tenemos 132 materias (11 materias base × 12 cursos)
        # Cada grupo de 11 materias consecutivas corresponde a un curso específico
        
        # Para cada curso (12 cursos: 1A, 1B, 2A, 2B, ..., 6A, 6B)
        for curso_id in range(1, 13):  # IDs de cursos del 1 al 12
            # Calcular el rango de materias para este curso específico
            # Curso 1 (1A) → materias 1-11
            # Curso 2 (1B) → materias 12-22
            # Curso 3 (2A) → materias 23-33
            # etc.
            inicio_materia = ((curso_id - 1) * 11) + 1
            fin_materia = curso_id * 11
            
            # Enlazar las 11 materias específicas de este curso
            for materia_id in range(inicio_materia, fin_materia + 1):
                materia_curso = MateriaCurso(
                    id=id_counter,
                    anio=anio_actual,
                    materia_id=materia_id,
                    curso_id=curso_id
                )
                materia_cursos.append(materia_curso)
                id_counter += 1
        
        try:
            for materia_curso in materia_cursos:
                db.session.add(materia_curso)
            db.session.commit()
            print(f"MateriaCurso: {len(materia_cursos)} relaciones creadas exitosamente")
            print("Cada materia específica ha sido enlazada solo con su curso correspondiente")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear relaciones MateriaCurso: {str(e)}")

def seed_estudiantes():
    # Check if table is empty
    if Estudiante.query.count() == 0:
        estudiantes = []
        
        # URLs de imágenes para hombres y mujeres
        imagen_masculina = {
            "url": "https://res.cloudinary.com/dozywphod/image/upload/v1748749405/cvtsafik3pkntiyvgpek.jpg",
            "public_id": "cvtsafik3pkntiyvgpek"
        }
        
        imagen_femenina = {
            "url": "https://res.cloudinary.com/dozywphod/image/upload/v1748749433/zt3anj0didaxukwotgib.jpg",
            "public_id": "zt3anj0didaxukwotgib"
        }
        
        # Nombres masculinos y femeninos
        nombres_masculinos = [
            "Carlos", "Diego", "Andrés", "Miguel", "José", "Luis", "David", "Juan", "Roberto", "Fernando",
            "Alejandro", "Ricardo", "Francisco", "Antonio", "Rafael", "Eduardo", "Sergio", "Javier", "Manuel", "Pedro",
            "Sebastián", "Gabriel", "Nicolás", "Mateo", "Santiago", "Daniel", "Emilio", "Gonzalo", "Rodrigo", "Héctor"
        ]
        
        nombres_femeninos = [
            "María", "Ana", "Carmen", "Rosa", "Elena", "Isabel", "Patricia", "Laura", "Andrea", "Mónica",
            "Claudia", "Sandra", "Beatriz", "Cristina", "Alejandra", "Verónica", "Natalia", "Gabriela", "Paola", "Fernanda",
            "Valeria", "Carolina", "Daniela", "Sofía", "Camila", "Lucía", "Valentina", "Isabella", "Martina", "Victoria"
        ]
        
        apellidos = [
            "García", "López", "Martínez", "González", "Rodríguez", "Fernández", "Sánchez", "Pérez", "Gómez", "Martín",
            "Jiménez", "Ruiz", "Hernández", "Díaz", "Moreno", "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez",
            "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez", "Serrano", "Blanco", "Suárez",
            "Molina", "Morales", "Ortega", "Delgado", "Castro", "Ortiz", "Rubio", "Marín", "Sanz", "Iglesias"
        ]
        
        apoderados = [
            "Carlos García Pérez", "María López Martínez", "José González Ruiz", "Ana Rodríguez Sánchez", "Luis Fernández Gómez",
            "Carmen Jiménez Martín", "David Hernández Díaz", "Rosa Moreno Muñoz", "Miguel Álvarez Romero", "Elena Alonso Gutiérrez",
            "Roberto Navarro Torres", "Isabel Domínguez Vázquez", "Fernando Ramos Gil", "Patricia Ramírez Serrano", "Alejandro Blanco Suárez"
        ]
        
        telefonos_base = ["70", "71", "72", "73", "74", "75", "76", "77", "78", "79"]
        
        ci_counter = 10000000  # Empezar con CIs desde 10,000,000
        
        # Para cada curso (12 cursos)
        for curso_num in range(1, 13):
            # Generar 25 estudiantes por curso
            for estudiante_num in range(1, 26):
                # Alternar entre masculino y femenino
                es_masculino = (estudiante_num % 2 == 1)
                
                if es_masculino:
                    nombre = random.choice(nombres_masculinos)
                    imagen_data = imagen_masculina
                else:
                    nombre = random.choice(nombres_femeninos)
                    imagen_data = imagen_femenina
                
                apellido1 = random.choice(apellidos)
                apellido2 = random.choice(apellidos)
                nombre_completo = f"{nombre} {apellido1} {apellido2}"
                
                # Generar fecha de nacimiento (estudiantes de 12-18 años)
                año_nacimiento = random.randint(2007, 2013)  # Para tener estudiantes de 12-18 años en 2025
                mes_nacimiento = random.randint(1, 12)
                dia_nacimiento = random.randint(1, 28)  # Usar 28 para evitar problemas con febrero
                fecha_nacimiento = date(año_nacimiento, mes_nacimiento, dia_nacimiento)
                
                # Generar teléfono
                telefono = random.choice(telefonos_base) + str(random.randint(100000, 999999))
                
                # Seleccionar apoderado
                apoderado = random.choice(apoderados)
                
                estudiante = Estudiante(
                    ci=ci_counter,
                    nombreCompleto=nombre_completo,
                    fechaNacimiento=fecha_nacimiento,
                    apoderado=apoderado,
                    telefono=telefono,
                    imagen_url=imagen_data["url"],
                    imagen_public_id=imagen_data["public_id"]
                )
                
                estudiantes.append(estudiante)
                ci_counter += 1
        
        try:
            for estudiante in estudiantes:
                db.session.add(estudiante)
            db.session.commit()
            print(f"Estudiantes creados exitosamente: {len(estudiantes)} estudiantes")
            print(f"25 estudiantes por cada uno de los 12 cursos")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear estudiantes: {str(e)}")

def seed_inscripciones():
    # Check if table is empty
    if Inscripcion.query.count() == 0:
        inscripciones = []
        id_counter = 1
        
        # Obtener todos los estudiantes ordenados por CI para tener un orden consistente
        estudiantes = Estudiante.query.order_by(Estudiante.ci).all()
        
        # Verificar que tenemos exactamente 300 estudiantes
        if len(estudiantes) != 300:
            print(f"Advertencia: Se esperaban 300 estudiantes, pero se encontraron {len(estudiantes)}")
            return
        
        # Fecha de inscripción (inicio del año escolar 2025)
        fecha_inscripcion = date(2025, 2, 1)  # 1 de febrero de 2025
        
        # Inscribir estudiantes: 25 por curso en orden secuencial
        # Estudiantes 1-25 → Curso 1 (1A)
        # Estudiantes 26-50 → Curso 2 (1B)
        # Estudiantes 51-75 → Curso 3 (2A)
        # etc.
        
        curso_id = 1
        estudiantes_en_curso_actual = 0
        
        for i, estudiante in enumerate(estudiantes):
            # Crear descripción basada en el curso
            curso_info = {
                1: "1A", 2: "1B", 3: "2A", 4: "2B", 5: "3A", 6: "3B",
                7: "4A", 8: "4B", 9: "5A", 10: "5B", 11: "6A", 12: "6B"
            }
            
            descripcion = f"Inscripción año escolar 2025 - Curso {curso_info[curso_id]}"
            
            inscripcion = Inscripcion(
                id=id_counter,
                descripcion=descripcion,
                fecha=fecha_inscripcion,
                estudiante_ci=estudiante.ci,
                curso_id=curso_id
            )
            
            inscripciones.append(inscripcion)
            id_counter += 1
            estudiantes_en_curso_actual += 1
            
            # Si ya tenemos 25 estudiantes en este curso, pasar al siguiente
            if estudiantes_en_curso_actual == 25:
                curso_id += 1
                estudiantes_en_curso_actual = 0
                
                # Si ya asignamos todos los cursos, salir del bucle
                if curso_id > 12:
                    break
        
        try:
            for inscripcion in inscripciones:
                db.session.add(inscripcion)
            db.session.commit()
            print(f"Inscripciones creadas exitosamente: {len(inscripciones)} inscripciones")
            print("Distribución: 25 estudiantes por cada uno de los 12 cursos")
            
            # Mostrar resumen de inscripciones por curso
            for curso_num in range(1, 13):
                curso_info = {
                    1: "1A", 2: "1B", 3: "2A", 4: "2B", 5: "3A", 6: "3B",
                    7: "4A", 8: "4B", 9: "5A", 10: "5B", 11: "6A", 12: "6B"
                }
                inicio = (curso_num - 1) * 25
                fin = curso_num * 25
                print(f"Curso {curso_info[curso_num]}: Estudiantes {inicio + 1} al {fin}")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear inscripciones: {str(e)}")
