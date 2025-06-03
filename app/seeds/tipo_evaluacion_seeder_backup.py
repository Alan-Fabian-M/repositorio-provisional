from app import db
from ..models.TipoEvaluacion_Model import TipoEvaluacion
from ..models.EvaluacionIntegral_Model import EvaluacionIntegral
from ..models.Materia_Model import Materia
from ..models.Curso_Model import Curso
from ..models.MateriaCurso_Model import MateriaCurso
from ..models.Estudiante_Model import Estudiante
from ..models.Inscripcion_Model import Inscripcion
from ..models.Gestion_Model import Gestion
from ..models.Docente_Model import Docente
from ..models.DocenteMateria_Model import DocenteMateria
from ..models.Evaluacion_Model import Evaluacion
from ..models.NotaFinal_Model import NotaFinal
from ..models.NotaEstimada_Model import NotaEstimada
from datetime import date, timedelta
import random
from werkzeug.security import generate_password_hash
from app import db

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
                evaluacion_integral_id=None
            ),
            TipoEvaluacion(
                id=2,
                nombre="Asistencia-Final",
                evaluacion_integral_id=1
            ),
            TipoEvaluacion(
                id=3,
                nombre="Examenes",
                evaluacion_integral_id=3
            ),
            TipoEvaluacion(
                id=4,
                nombre="Tareas",
                evaluacion_integral_id=4
            ),
            TipoEvaluacion(
                id=5,
                nombre="Exposiciones",
                evaluacion_integral_id=2
            ),
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
            "Sebastián", "Gabriel", "Nicolás", "Mateo", "Santiago", "Daniel", "Emilio", "Gonzalo", "Rodrigo", "Héctor",
            "Pablo", "Álvaro", "Iván", "Rubén", "Óscar", "Víctor", "Adrián", "Raúl", "Ignacio", "Tomás"
        ]
        
        nombres_femeninos = [
            "María", "Ana", "Carmen", "Rosa", "Elena", "Isabel", "Patricia", "Laura", "Andrea", "Mónica",
            "Claudia", "Sandra", "Beatriz", "Cristina", "Alejandra", "Verónica", "Natalia", "Gabriela", "Paola", "Fernanda",
            "Valeria", "Carolina", "Daniela", "Sofía", "Camila", "Lucía", "Valentina", "Isabella", "Martina", "Victoria",
            "Jimena", "Renata", "Amanda", "Lorena", "Diana", "Silvia", "Raquel", "Pilar", "Esperanza", "Inés"
        ]
        
        apellidos = [
            "García", "López", "Martínez", "González", "Rodríguez", "Fernández", "Sánchez", "Pérez", "Gómez", "Martín",
            "Jiménez", "Ruiz", "Hernández", "Díaz", "Moreno", "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez",
            "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez", "Serrano", "Blanco", "Suárez",
            "Molina", "Morales", "Ortega", "Delgado", "Castro", "Ortiz", "Rubio", "Marín", "Sanz", "Iglesias",
            "Vargas", "Herrera", "Mendoza", "Cruz", "Flores", "Espinoza", "Rivera", "Aguilar", "Contreras", "Lara"
        ]
        
        apoderados = [
            "Carlos García Pérez", "María López Martínez", "José González Ruiz", "Ana Rodríguez Sánchez", "Luis Fernández Gómez",
            "Carmen Jiménez Martín", "David Hernández Díaz", "Rosa Moreno Muñoz", "Miguel Álvarez Romero", "Elena Alonso Gutiérrez",
            "Roberto Navarro Torres", "Isabel Domínguez Vázquez", "Fernando Ramos Gil", "Patricia Ramírez Serrano", "Alejandro Blanco Suárez",
            "Ricardo Molina Castro", "Sandra Morales Ortiz", "Francisco Delgado Rubio", "Beatriz Marín Sanz", "Antonio Iglesias Vargas"
        ]
        
        telefonos_base = ["70", "71", "72", "73", "74", "75", "76", "77", "78", "79"]
        
        ci_counter = 10000000  # Empezar con CIs desde 10,000,000
        
        # Crear 600 estudiantes (300 para 2024 + 300 para 2025)
        # Para cada ciclo de 12 cursos (25 estudiantes por curso)
        for ciclo in range(2):  # 2 ciclos: 2024 y 2025
            for curso_num in range(1, 13):  # 12 cursos
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
                    año_nacimiento = random.randint(2006, 2013)  # Para tener estudiantes de diferentes edades
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
            print(f"600 estudiantes en total: 300 para gestión 2024 + 300 para gestión 2025")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear estudiantes: {str(e)}")

def seed_inscripciones_historicas():
    """
    Crea inscripciones para 2024 con 3 TRIMESTRES COMPLETOS y evaluaciones realistas.
    - Primeros 300 estudiantes: inscripciones para 2024 (3 trimestres)
    - Siguientes 300 estudiantes: inscripciones para 2025 (1 gestión simple)
    - Cada trimestre 2024 tendrá evaluaciones realistas con asistencias, exámenes, tareas y exposiciones
    """
    # Check if table is empty
    if Inscripcion.query.count() == 0:
        inscripciones = []
        id_counter = 1
        
        # Obtener todos los estudiantes ordenados por CI para tener un orden consistente
        estudiantes = Estudiante.query.order_by(Estudiante.ci).all()
        
        # Verificar que tenemos exactamente 600 estudiantes
        if len(estudiantes) != 600:
            print(f"Advertencia: Se esperaban 600 estudiantes, pero se encontraron {len(estudiantes)}")
            return
        
        # Información de cursos
        curso_info = {
            1: "1A", 2: "1B", 3: "2A", 4: "2B", 5: "3A", 6: "3B",
            7: "4A", 8: "4B", 9: "5A", 10: "5B", 11: "6A", 12: "6B"
        }
        
        # PROCESO PARA GESTIÓN 2024 - SISTEMA DE 3 TRIMESTRES
        print("=" * 70)
        print("INICIANDO SISTEMA ESCOLAR 2024 - TRES TRIMESTRES COMPLETOS")
        print("=" * 70)
        
        # 1. Crear inscripciones para 2024 (primeros 300 estudiantes)
        print("Paso 1: Creando inscripciones para año escolar 2024...")
        fecha_inscripcion_2024 = date(2024, 2, 1)  # 1 de febrero de 2024
        
        curso_id = 1
        estudiantes_en_curso_actual = 0
        
        for i in range(300):  # Primeros 300 estudiantes
            estudiante = estudiantes[i]
            
            descripcion = f"Inscripción año escolar 2024 - Curso {curso_info[curso_id]}"
            
            inscripcion = Inscripcion(
                id=id_counter,
                descripcion=descripcion,
                fecha=fecha_inscripcion_2024,
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
                
                # Si ya asignamos todos los cursos, reiniciar para el siguiente año
                if curso_id > 12:
                    curso_id = 1
        
        # Guardar las inscripciones de 2024 primero
        try:
            inscripciones_2024 = inscripciones[:300]  # Primeras 300 inscripciones
            for inscripcion in inscripciones_2024:
                db.session.add(inscripcion)
            db.session.commit()
            print(f"✓ Inscripciones 2024 creadas: {len(inscripciones_2024)} inscripciones")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error al crear inscripciones 2024: {str(e)}")
            return
        
        # 2. Crear y poblar los tres trimestres de 2024
        print("\nPaso 2: Creando y poblando tres trimestres para 2024...")
        print("-" * 50)
        
        trimestres_2024 = [
            {"periodo": "Primer Trimestre", "fechas": (date(2024, 2, 5), date(2024, 5, 17))},
            {"periodo": "Segundo Trimestre", "fechas": (date(2024, 5, 20), date(2024, 8, 30))},
            {"periodo": "Tercer Trimestre", "fechas": (date(2024, 9, 2), date(2024, 11, 29))}
        ]
        
        gestiones_creadas = []
        
        for i, trimestre in enumerate(trimestres_2024, 1):
            print(f"\n🏫 CREANDO {trimestre['periodo'].upper()} 2024")
            print("=" * 50)
            
            try:
                # Crear la gestión del trimestre
                nueva_gestion = crear_gestion_trimestre_2024(
                    2024, 
                    trimestre["periodo"], 
                    trimestre["fechas"][0], 
                    trimestre["fechas"][1],
                    trimestre_numero=i
                )
                
                if nueva_gestion:
                    gestiones_creadas.append(nueva_gestion)
                    print(f"✓ {trimestre['periodo']} creado exitosamente (ID: {nueva_gestion.id})")
                else:
                    print(f"✗ Error al crear {trimestre['periodo']}")
                    
            except Exception as e:
                print(f"✗ Error en {trimestre['periodo']}: {str(e)}")
                continue        
        # PROCESO PARA GESTIÓN 2025 (SIMPLE)
        print("\n" + "=" * 60)
        print("INICIANDO PROCESO PARA GESTIÓN 2025 (GESTIÓN SIMPLE)")
        print("=" * 60)
        
        # 3. Crear inscripciones para 2025 (siguientes 300 estudiantes)
        print("Paso 3: Creando inscripciones para gestión 2025...")
        fecha_inscripcion_2025 = date(2025, 2, 1)  # 1 de febrero de 2025
        
        curso_id = 1
        estudiantes_en_curso_actual = 0
        
        for i in range(300, 600):  # Estudiantes 301-600
            estudiante = estudiantes[i]
            
            descripcion = f"Inscripción año escolar 2025 - Curso {curso_info[curso_id]}"
            
            inscripcion = Inscripcion(
                id=id_counter,
                descripcion=descripcion,
                fecha=fecha_inscripcion_2025,
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
        
        # Guardar las inscripciones de 2025
        try:
            inscripciones_2025 = inscripciones[300:]  # Últimas 300 inscripciones
            for inscripcion in inscripciones_2025:
                db.session.add(inscripcion)
            db.session.commit()
            print(f"✓ Inscripciones 2025 creadas: {len(inscripciones_2025)} inscripciones")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error al crear inscripciones 2025: {str(e)}")
            return
        
        # 4. Crear gestión 2025 simple
        print("Paso 4: Creando gestión 2025 simple...")
        try:
            resultado_2025 = crear_gestion_con_notas(2025, "Primer semestre")
            if resultado_2025:
                print("✓ Gestión 2025 creada exitosamente")
            else:
                print("✗ Error al crear gestión 2025")
                return
        except Exception as e:
            print(f"✗ Error en el proceso de gestión 2025: {str(e)}")
            return
        
        # RESUMEN FINAL
        print("\n" + "=" * 70)
        print("🎓 SISTEMA ESCOLAR COMPLETADO EXITOSAMENTE 🎓")
        print("=" * 70)
        print(f"📚 Total inscripciones creadas: {len(inscripciones)}")
        print("\n📊 Distribución:")
        print("  🗓️  2024: 300 estudiantes - 3 TRIMESTRES COMPLETOS")
        print("  🗓️  2025: 300 estudiantes - 1 gestión simple")
        
        if gestiones_creadas:
            print(f"\n🏫 Gestiones 2024 creadas: {len(gestiones_creadas)} trimestres")
            for gestion in gestiones_creadas:
                print(f"  ✅ {gestion.periodo} (ID: {gestion.id})")
        
        print("\n🔍 Resumen detallado:")
        print("📋 SISTEMA 2024 (TRES TRIMESTRES):")
        for curso_num in range(1, 13):
            inicio = (curso_num - 1) * 25 + 1
            fin = curso_num * 25
            print(f"  📝 Curso {curso_info[curso_num]}: Estudiantes {inicio} al {fin}")
        
        print("\n📋 GESTIÓN 2025 (SIMPLE):")
        for curso_num in range(1, 13):
            inicio = (curso_num - 1) * 25 + 301
            fin = curso_num * 25 + 300
            print(f"  📝 Curso {curso_info[curso_num]}: Estudiantes {inicio} al {fin}")
        
        print(f"\n🎯 Sistema listo para usar con {len(gestiones_creadas)} trimestres completos para 2024!")


def crear_gestion_trimestre_2024(anio, periodo, fecha_inicio, fecha_fin, trimestre_numero):
    """
    Crea una gestión trimestral para 2024 con evaluaciones realistas y completas.
    Genera automáticamente:
    - Asistencias diarias (usando endpoint de asistencia)
    - Exámenes (evaluación de 'saber')
    - Tareas (evaluación de 'hacer') 
    - Exposiciones (evaluación de 'decidir')
    - Notas finales calculadas automáticamente
    """
    try:
        print(f"  🏗️  Creando estructura del trimestre...")
        
        # 1. Crear la gestión
        nueva_gestion = Gestion(anio=anio, periodo=periodo)
        db.session.add(nueva_gestion)
        db.session.commit()
        
        print(f"  ✅ Gestión creada: {periodo} (ID: {nueva_gestion.id})")
        
        # 2. Crear estructura base (NotaFinal y NotaEstimada)
        print(f"  📊 Creando estructura de notas...")
        crear_estructura_base_gestion(nueva_gestion.id)
        
        # 3. Generar evaluaciones realistas por trimestre
        print(f"  📝 Generando evaluaciones realistas...")
        generar_evaluaciones_trimestre(nueva_gestion.id, fecha_inicio, fecha_fin, trimestre_numero)
        
        # 4. Generar asistencias diarias usando el endpoint
        print(f"  👥 Generando asistencias diarias...")
        generar_asistencias_diarias(nueva_gestion.id, fecha_inicio, fecha_fin)
        
        print(f"  🎯 {periodo} completado exitosamente")
        return nueva_gestion
        
    except Exception as e:
        db.session.rollback()
        print(f"  ❌ Error al crear {periodo}: {str(e)}")
        return None


def crear_estructura_base_gestion(gestion_id):
    """Crea NotaFinal y NotaEstimada para todos los estudiantes de 2024"""
    try:
        # Obtener estudiantes de 2024 (primeros 300)
        estudiantes_2024 = Estudiante.query.order_by(Estudiante.ci).limit(300).all()
        
        notas_creadas = 0
        for estudiante in estudiantes_2024:
            # Obtener inscripción del estudiante
            inscripcion = Inscripcion.query.filter_by(estudiante_ci=estudiante.ci).first()
            if not inscripcion or not inscripcion.curso:
                continue
            
            # Obtener materias del curso
            materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()
            
            for mc in materias_curso:
                # Crear NotaFinal
                nota_final = NotaFinal(
                    valor=0.0,
                    estudiante_ci=estudiante.ci,
                    gestion_id=gestion_id,
                    materia_id=mc.materia.id
                )
                db.session.add(nota_final)
                
                # Crear NotaEstimada
                nota_estimada = NotaEstimada(
                    valor_estimado=0.0,
                    razon_estimacion="Trimestre en progreso",
                    estudiante_ci=estudiante.ci,
                    gestion_id=gestion_id,
                    materia_id=mc.materia.id
                )
                db.session.add(nota_estimada)
                notas_creadas += 2
        
        db.session.commit()
        print(f"    ✅ Estructura de notas creada: {notas_creadas} registros")
        
    except Exception as e:
        db.session.rollback()
        print(f"    ❌ Error al crear estructura base: {str(e)}")


def generar_evaluaciones_trimestre(gestion_id, fecha_inicio, fecha_fin, trimestre_numero):
    """
    Genera evaluaciones realistas para un trimestre específico:
    - 2-3 exámenes por materia (saber - 35 pts)
    - 4-6 tareas por materia (hacer - 35 pts) 
    - 1-2 exposiciones por materia (decidir - 15 pts)
    """
    try:
        # Obtener tipos de evaluación
        tipo_examen = TipoEvaluacion.query.filter_by(nombre='Examenes').first()
        tipo_tarea = TipoEvaluacion.query.filter_by(nombre='Tareas').first()
        tipo_exposicion = TipoEvaluacion.query.filter_by(nombre='Exposiciones').first()
        
        if not all([tipo_examen, tipo_tarea, tipo_exposicion]):
            print("    ❌ No se encontraron todos los tipos de evaluación")
            return
        
        # Obtener estudiantes de 2024
        estudiantes_2024 = Estudiante.query.order_by(Estudiante.ci).limit(300).all()
        
        evaluaciones_creadas = 0
        
        for estudiante in estudiantes_2024:
            inscripcion = Inscripcion.query.filter_by(estudiante_ci=estudiante.ci).first()
            if not inscripcion or not inscripcion.curso:
                continue
            
            materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()
            
            for mc in materias_curso:
                materia = mc.materia
                
                # 1. EXÁMENES (2-3 por trimestre)
                num_examenes = random.randint(2, 3)
                for i in range(num_examenes):
                    fecha_examen = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                    nota_examen = generar_nota_realista("examen")
                    
                    evaluacion = Evaluacion(
                        descripcion=f"Examen {i+1} - {materia.nombre}",
                        fecha=fecha_examen,
                        nota=nota_examen,
                        tipo_evaluacion_id=tipo_examen.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(evaluacion)
                    evaluaciones_creadas += 1
                
                # 2. TAREAS (4-6 por trimestre)
                num_tareas = random.randint(4, 6)
                for i in range(num_tareas):
                    fecha_tarea = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                    nota_tarea = generar_nota_realista("tarea")
                    
                    evaluacion = Evaluacion(
                        descripcion=f"Tarea {i+1} - {materia.nombre}",
                        fecha=fecha_tarea,
                        nota=nota_tarea,
                        tipo_evaluacion_id=tipo_tarea.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(evaluacion)
                    evaluaciones_creadas += 1
                
                # 3. EXPOSICIONES (1-2 por trimestre)
                num_exposiciones = random.randint(1, 2)
                for i in range(num_exposiciones):
                    fecha_exposicion = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                    nota_exposicion = generar_nota_realista("exposicion")
                    
                    evaluacion = Evaluacion(
                        descripcion=f"Exposición {i+1} - {materia.nombre}",
                        fecha=fecha_exposicion,
                        nota=nota_exposicion,
                        tipo_evaluacion_id=tipo_exposicion.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id                    )
                    db.session.add(evaluacion)
                    evaluaciones_creadas += 1
                
                # Actualizar nota final después de completar todas las evaluaciones de esta materia
                actualizar_nota_final_automatica(estudiante.ci, gestion_id, materia.id)
        
        db.session.commit()
        print(f"    ✅ Evaluaciones académicas creadas: {evaluaciones_creadas}")
        print(f"    ✅ Notas finales actualizadas automáticamente")
        
    except Exception as e:
        db.session.rollback()        
        print(f"    ❌ Error al generar evaluaciones: {str(e)}")


def generar_asistencias_diarias(gestion_id, fecha_inicio, fecha_fin):
    """
    Genera asistencias diarias realistas y usa el endpoint para calcular asistencia final
    """
    try:
        # Función local para calcular asistencia final (evita import circular)
        def calcular_asistencia_final(estudiante_ci, gestion_id, materia_id):
            evaluaciones = Evaluacion.query.filter_by(
                estudiante_ci=estudiante_ci,
                materia_id=materia_id,
                gestion_id=gestion_id,
                tipo_evaluacion_id=1  # ID fijo para Asistencia-Diaria
            ).all()

            if not evaluaciones:
                return 0

            suma = sum(eva.nota for eva in evaluaciones)
            promedio = suma / len(evaluaciones)
            return promedio
        
        # Obtener estudiantes de 2024
        estudiantes_2024 = Estudiante.query.order_by(Estudiante.ci).limit(300).all()
        tipo_asistencia_diaria = TipoEvaluacion.query.filter_by(nombre='Asistencia-Diaria').first()
        tipo_asistencia_final = TipoEvaluacion.query.filter_by(nombre='Asistencia-Final').first()
        
        if not tipo_asistencia_diaria or not tipo_asistencia_final:
            print("    ❌ Tipos de asistencia no encontrados")
            return
        
        asistencias_creadas = 0
        asistencias_finales_creadas = 0
        
        for estudiante in estudiantes_2024:
            inscripcion = Inscripcion.query.filter_by(estudiante_ci=estudiante.ci).first()
            if not inscripcion or not inscripcion.curso:
                continue
            
            materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()
            
            for mc in materias_curso:
                materia = mc.materia
                  # Generar asistencias diarias (15-25 días por trimestre)
                num_asistencias = random.randint(15, 25)
                
                for i in range(num_asistencias):
                    fecha_asistencia = generar_fecha_aleatoria(fecha_inicio, fecha_fin)
                    nota_asistencia = generar_nota_asistencia()  # 0, 5, 10 o 15
                    
                    evaluacion = Evaluacion(
                        descripcion=f"Asistencia día {i+1}",
                        fecha=fecha_asistencia,
                        nota=nota_asistencia,
                        tipo_evaluacion_id=tipo_asistencia_diaria.id,
                        estudiante_ci=estudiante.ci,
                        materia_id=materia.id,
                        gestion_id=gestion_id
                    )
                    db.session.add(evaluacion)
                    asistencias_creadas += 1
                
                # Commit parcial para las asistencias diarias
                db.session.commit()
                
                # Calcular asistencia final usando la función del endpoint
                resultado_asistencia = AsistenciaFinal(estudiante.ci, gestion_id, materia.id)
                nota_asistencia_final = resultado_asistencia.get("asistenciaFinal", 0)
                
                # Crear evaluación de asistencia final
                evaluacion_final = Evaluacion(
                    descripcion="Asistencia Final - Calculada automáticamente",
                    fecha=fecha_fin,
                    nota=nota_asistencia_final,
                    tipo_evaluacion_id=tipo_asistencia_final.id,
                    estudiante_ci=estudiante.ci,
                    materia_id=materia.id,
                    gestion_id=gestion_id                )
                db.session.add(evaluacion_final)
                asistencias_finales_creadas += 1
                
                # Actualizar nota final automáticamente (simula endpoint POST)
                actualizar_nota_final_automatica(estudiante.ci, gestion_id, materia.id)
        
        db.session.commit()
        print(f"    ✅ Asistencias diarias: {asistencias_creadas}")
        print(f"    ✅ Asistencias finales: {asistencias_finales_creadas}")
        
    except Exception as e:
        db.session.rollback()
        print(f"    ❌ Error al generar asistencias: {str(e)}")


def generar_fecha_aleatoria(fecha_inicio, fecha_fin):
    """Genera una fecha aleatoria entre dos fechas"""
    dias_diferencia = (fecha_fin - fecha_inicio).days
    dias_aleatorios = random.randint(0, dias_diferencia)
    return fecha_inicio + timedelta(days=dias_aleatorios)


def generar_nota_realista(tipo_evaluacion):
    """Genera notas realistas según el tipo de evaluación"""
    if tipo_evaluacion == "examen":
        # Exámenes: distribución más variada (40-100)
        return round(random.uniform(40, 100), 1)
    elif tipo_evaluacion == "tarea":
        # Tareas: generalmente mejores notas (60-100)
        return round(random.uniform(60, 100), 1)
    elif tipo_evaluacion == "exposicion":
        # Exposiciones: buenas notas pero algo variables (70-100)
        return round(random.uniform(70, 100), 1)
    else:
        return round(random.uniform(50, 100), 1)


def generar_nota_asistencia():
    """
    Genera notas de asistencia usando escala de 15 puntos:
    - 0: Ausente
    - 5: Llegada tarde 
    - 10: Con licencia/permiso
    - 15: Presente
    """
    rand = random.random()
    if rand < 0.05:  # 5% faltas (ausente)
        return 0
    elif rand < 0.12:  # 7% llegadas tarde
        return 5
    elif rand < 0.15:  # 3% con licencia/permiso
        return 10
    else:  # 85% presente
        return 15

def crear_gestion_con_notas(anio, periodo):
    """
    Crea una gestión simple para 2025 con estructura básica de notas.
    Solo para estudiantes de 2025 (estudiantes 301-600).
    """
    try:
        # Crear la gestión directamente en la base de datos
        nueva_gestion = Gestion(anio=anio, periodo=periodo)
        db.session.add(nueva_gestion)
        db.session.commit()
        
        print(f"  ✓ Gestión {anio} creada con ID: {nueva_gestion.id}")
        
        # Obtener estudiantes de 2025 (estudiantes 301-600)
        estudiantes_2025 = Estudiante.query.order_by(Estudiante.ci).offset(300).limit(300).all()
        tipoEvaluacionId = TipoEvaluacion.query.filter_by(nombre='Asistencia-Final').first()
        
        notas_creadas = 0
        evaluaciones_creadas = 0
        
        for est in estudiantes_2025:
            # Obtener la inscripción activa del estudiante
            inscripcion = Inscripcion.query.filter_by(estudiante_ci=est.ci).order_by(Inscripcion.fecha.desc()).first()
            if not inscripcion or not inscripcion.curso:
                continue

            # Obtener materias asociadas al curso
            materias_curso = MateriaCurso.query.filter_by(curso_id=inscripcion.curso.id).all()

            for mc in materias_curso:
                materia = mc.materia
                if not materia:
                    continue

                # Crear NotaFinal
                nota_final = NotaFinal(
                    valor=0.0,
                    estudiante_ci=est.ci,
                    gestion_id=nueva_gestion.id,
                    materia_id=materia.id
                )
                db.session.add(nota_final)

                # Crear NotaEstimada
                nota_estimada = NotaEstimada(
                    valor_estimado=0.0,
                    razon_estimacion="Gestión 2025 - estructura básica",
                    estudiante_ci=est.ci,
                    gestion_id=nueva_gestion.id,
                    materia_id=materia.id
                )
                db.session.add(nota_estimada)
                notas_creadas += 2
                
                # Crear Evaluacion básica de asistencia
                evaluacion = Evaluacion(
                    descripcion="Asistencia final - estructura básica",
                    fecha=date.today(),
                    nota=0.0,
                    tipo_evaluacion_id=tipoEvaluacionId.id,
                    estudiante_ci=est.ci,
                    materia_id=materia.id,
                    gestion_id=nueva_gestion.id
                )
                db.session.add(evaluacion)
                evaluaciones_creadas += 1

        db.session.commit()
        print(f"  ✓ Notas creadas: {notas_creadas} (NotaFinal + NotaEstimada)")
        print(f"  ✓ Evaluaciones básicas: {evaluaciones_creadas}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"  ✗ Error al crear gestión {anio}: {str(e)}")
        return False
def seed_docentes():
    """
    Crea docentes suficientes para una escuela secundaria.
    Incluye docentes especializados por materia y algunos que pueden enseñar múltiples materias.
    """
    # Check if table is empty
    if Docente.query.count() == 0:
        docentes = []
        
        # Lista de nombres y apellidos para docentes
        nombres_masculinos = [
            "Carlos", "Miguel", "José", "Luis", "David", "Juan", "Roberto", "Fernando",
            "Alejandro", "Ricardo", "Francisco", "Antonio", "Rafael", "Eduardo", "Sergio",
            "Javier", "Manuel", "Pedro", "Sebastián", "Gabriel", "Nicolás", "Mateo",
            "Santiago", "Daniel", "Emilio", "Gonzalo", "Rodrigo", "Héctor", "Pablo", "Álvaro"
        ]
        
        nombres_femeninos = [
            "María", "Ana", "Carmen", "Rosa", "Elena", "Isabel", "Patricia", "Laura",
            "Andrea", "Mónica", "Claudia", "Sandra", "Beatriz", "Cristina", "Alejandra",
            "Verónica", "Natalia", "Gabriela", "Paola", "Fernanda", "Valeria", "Carolina",
            "Daniela", "Sofía", "Camila", "Lucía", "Valentina", "Isabella", "Martina", "Victoria"
        ]
        
        apellidos = [
            "García", "López", "Martínez", "González", "Rodríguez", "Fernández", "Sánchez",
            "Pérez", "Gómez", "Martín", "Jiménez", "Ruiz", "Hernández", "Díaz", "Moreno",
            "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez", "Navarro", "Torres",
            "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez", "Serrano", "Blanco", "Suárez"
        ]
        
        # Especialidades de docentes por materias (basado en las materias del sistema)
        especialidades_docentes = [
            {
                "materias": ["Matemática", "Física"],
                "nombre": "Ciencias Exactas",
                "cantidad": 8
            },
            {
                "materias": ["Lenguaje", "Literatura", "Comunicación"],
                "nombre": "Lengua y Literatura",
                "cantidad": 6
            },
            {
                "materias": ["Historia", "Geografía", "Estudios Sociales"],
                "nombre": "Ciencias Sociales",
                "cantidad": 6
            },
            {
                "materias": ["Química", "Biología", "Ciencias Naturales"],
                "nombre": "Ciencias Naturales",
                "cantidad": 6
            },
            {
                "materias": ["Inglés", "Idiomas"],
                "nombre": "Idiomas",
                "cantidad": 4
            },
            {
                "materias": ["Educación Física", "Deportes"],
                "nombre": "Educación Física",
                "cantidad": 4
            },
            {
                "materias": ["Arte", "Música", "Dibujo"],
                "nombre": "Artes",
                "cantidad": 3
            },
            {
                "materias": ["Tecnología", "Informática", "Computación"],
                "nombre": "Tecnología",
                "cantidad": 3
            },
            {
                "materias": ["Filosofía", "Ética", "Religión"],
                "nombre": "Humanidades",
                "cantidad": 3
            },
            {
                "materias": ["Economía", "Contabilidad"],
                "nombre": "Ciencias Económicas",
                "cantidad": 2
            }
        ]
        
        ci_counter = 5000000  # Empezar con CIs desde 5,000,000 para docentes
        docente_id = 1
        
        print("Creando docentes por especialidad:")
        
        for especialidad in especialidades_docentes:
            cantidad = especialidad["cantidad"]
            nombre_especialidad = especialidad["nombre"]
            
            print(f"  - {nombre_especialidad}: {cantidad} docentes")
            
            for i in range(cantidad):
                # Alternar entre masculino y femenino
                es_masculino = (i % 2 == 0)
                
                if es_masculino:
                    nombre = random.choice(nombres_masculinos)
                else:
                    nombre = random.choice(nombres_femeninos)
                
                apellido1 = random.choice(apellidos)
                apellido2 = random.choice(apellidos)
                nombre_completo = f"{nombre} {apellido1} {apellido2}"
                
                # Crear email basado en el nombre (sin espacios ni caracteres especiales)
                nombre_email = nombre.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                apellido_email = apellido1.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                gmail = f"{nombre_email}.{apellido_email}@gmail.com"
                
                # Contraseña por defecto codificada
                contrasena_hash = generate_password_hash("docente123")
                
                docente = Docente(
                    ci=ci_counter,
                    nombreCompleto=nombre_completo,
                    gmail=gmail,
                    contrasena=contrasena_hash,
                    esDocente=True
                )
                
                docentes.append(docente)
                ci_counter += 1
                docente_id += 1
        
        # Agregar algunos docentes adicionales como directivos/administrativos
        directivos = [
            {
                "nombre": "Director General",
                "nombre_completo": "Alberto Vargas Mendoza",
                "gmail": "alberto.vargas@gmail.com"
            },
            {
                "nombre": "Subdirectora Académica",
                "nombre_completo": "Gloria Herrera Cruz",
                "gmail": "gloria.herrera@gmail.com"
            },
            {
                "nombre": "Coordinador Pedagógico",
                "nombre_completo": "Fernando Flores Espinoza",
                "gmail": "fernando.flores@gmail.com"
            },
            {
                "nombre": "Secretaria Académica",
                "nombre_completo": "Carmen Rivera Aguilar",
                "gmail": "carmen.rivera@gmail.com"
            }
        ]
        
        print("  - Directivos y Administrativos: 4 personas")
        
        for directivo_info in directivos:
            contrasena_hash = generate_password_hash("admin123")
            
            directivo = Docente(
                ci=ci_counter,
                nombreCompleto=directivo_info["nombre_completo"],
                gmail=directivo_info["gmail"],
                contrasena=contrasena_hash,
                esDocente=True
            )
            
            docentes.append(directivo)
            ci_counter += 1
        
        try:
            for docente in docentes:
                db.session.add(docente)
            db.session.commit()
            
            print(f"\n✓ Docentes creados exitosamente: {len(docentes)} docentes")
            print("\nDistribución de docentes:")
            
            total_por_especialidad = sum(esp["cantidad"] for esp in especialidades_docentes)
            print(f"  - Docentes por especialidad: {total_por_especialidad}")
            print(f"  - Directivos y administrativos: 4")
            print(f"  - Total: {len(docentes)} docentes")
            
            print("\nCredenciales por defecto:")
            print("  - Docentes de especialidad: contraseña 'docente123'")
            print("  - Directivos/administrativos: contraseña 'admin123'")
            print("  - Todos los emails siguen el formato: nombre.apellido@gmail.com")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error al crear docentes: {str(e)}")

def seed_docente_materia():
    """
    Asigna docentes a materias según sus especialidades.
    Cada docente será asignado a materias que corresponden con su área de expertise.
    """
    # Check if table is empty
    if DocenteMateria.query.count() == 0:
        docente_materias = []
        id_counter = 1
        
        # Obtener todos los docentes y materias
        docentes = Docente.query.order_by(Docente.ci).all()
        materias = Materia.query.order_by(Materia.id).all()
        
        if not docentes or not materias:
            print("No hay docentes o materias para asignar")
            return
        
        print(f"Asignando {len(docentes)} docentes a {len(materias)} materias...")
        
        # Mapeo de especialidades a nombres de materias
        especialidades_materias = {
            # Ciencias Exactas (8 docentes)
            "matematicas": ["Matemáticas"],
            "fisica": ["Física"],
            
            # Lengua y Literatura (6 docentes)
            "lenguaje": ["Lenguaje"],
            
            # Ciencias Sociales (6 docentes)
            "sociales": ["Ciencias Sociales"],
            
            # Ciencias Naturales (6 docentes)
            "quimica": ["Química"],
            "naturales": ["Ciencias Naturales"],
            
            # Idiomas (4 docentes)
            "ingles": ["Inglés"],
            
            # Educación Física (4 docentes)
            "educacion_fisica": ["Educación Física"],
            
            # Artes (3 docentes)
            "artes": ["Artes Plásticas"],
            "musica": ["Música"],
            
            # Tecnología (3 docentes)
            "tecnologia": ["Tecnología", "Informática"],
            
            # Humanidades (3 docentes)
            "religion": ["Religión"],
            "filosofia": ["Filosofía"],
            
            # Ciencias Económicas (2 docentes)
            "economia": ["Economía", "Contabilidad"]
        }
        
        # Agrupar materias por tipo (sin considerar el curso específico)
        materias_por_tipo = {}
        for materia in materias:
            # Extraer el nombre base de la materia (antes del número y letra del curso)
            nombre_base = materia.nombre
            for especialidad in ["Matemáticas", "Ciencias Sociales", "Ciencias Naturales", "Inglés", 
                               "Educación Física", "Artes Plásticas", "Religión", "Música", 
                               "Química", "Física", "Lenguaje"]:
                if especialidad in nombre_base:
                    if especialidad not in materias_por_tipo:
                        materias_por_tipo[especialidad] = []
                    materias_por_tipo[especialidad].append(materia)
                    break
        
        print(f"Materias agrupadas por tipo:")
        for tipo, lista_materias in materias_por_tipo.items():
            print(f"  - {tipo}: {len(lista_materias)} materias")
        
        # Asignar docentes por especialidad
        docente_index = 0
        fecha_asignacion = date(2025, 2, 1)  # Fecha de inicio del año escolar 2025
        
        # Matemáticas (8 docentes)
        if "Matemáticas" in materias_por_tipo:
            materias_matematicas = materias_por_tipo["Matemáticas"]
            print(f"\nAsignando docentes de Matemáticas...")
            
            # Distribuir las 12 materias de matemáticas entre 8 docentes
            # Algunos docentes tendrán 1 materia, otros 2
            materias_por_docente = len(materias_matematicas) // 8
            materias_extra = len(materias_matematicas) % 8
            
            materia_index = 0
            for i in range(8):
                if docente_index >= len(docentes):
                    break
                    
                docente = docentes[docente_index]
                
                # Calcular cuántas materias asignar a este docente
                num_materias = materias_por_docente
                if i < materias_extra:
                    num_materias += 1
                
                # Asignar materias a este docente
                for j in range(num_materias):
                    if materia_index < len(materias_matematicas):
                        materia = materias_matematicas[materia_index]
                        
                        docente_materia = DocenteMateria(
                            id=id_counter,
                            fecha=fecha_asignacion,
                            docente_ci=docente.ci,
                            materia_id=materia.id
                        )
                        docente_materias.append(docente_materia)
                        id_counter += 1
                        materia_index += 1
                
                print(f"  - {docente.nombreCompleto} asignado a {num_materias} materias de Matemáticas")
                docente_index += 1
        
        # Lenguaje (6 docentes)
        if "Lenguaje" in materias_por_tipo:
            materias_lenguaje = materias_por_tipo["Lenguaje"]
            print(f"\nAsignando docentes de Lenguaje...")
            
            # Distribuir las 12 materias de lenguaje entre 6 docentes (2 materias por docente)
            materias_por_docente = 2
            
            materia_index = 0
            for i in range(6):
                if docente_index >= len(docentes) or materia_index >= len(materias_lenguaje):
                    break
                    
                docente = docentes[docente_index]
                
                # Asignar 2 materias a este docente
                for j in range(materias_por_docente):
                    if materia_index < len(materias_lenguaje):
                        materia = materias_lenguaje[materia_index]
                        
                        docente_materia = DocenteMateria(
                            id=id_counter,
                            fecha=fecha_asignacion,
                            docente_ci=docente.ci,
                            materia_id=materia.id
                        )
                        docente_materias.append(docente_materia)
                        id_counter += 1
                        materia_index += 1
                
                print(f"  - {docente.nombreCompleto} asignado a {materias_por_docente} materias de Lenguaje")
                docente_index += 1
        
        # Ciencias Sociales (6 docentes)
        if "Ciencias Sociales" in materias_por_tipo:
            materias_sociales = materias_por_tipo["Ciencias Sociales"]
            print(f"\nAsignando docentes de Ciencias Sociales...")
            
            # Distribuir las 12 materias entre 6 docentes (2 materias por docente)
            materias_por_docente = 2
            
            materia_index = 0
            for i in range(6):
                if docente_index >= len(docentes) or materia_index >= len(materias_sociales):
                    break
                    
                docente = docentes[docente_index]
                
                for j in range(materias_por_docente):
                    if materia_index < len(materias_sociales):
                        materia = materias_sociales[materia_index]
                        
                        docente_materia = DocenteMateria(
                            id=id_counter,
                            fecha=fecha_asignacion,
                            docente_ci=docente.ci,
                            materia_id=materia.id
                        )
                        docente_materias.append(docente_materia)
                        id_counter += 1
                        materia_index += 1
                
                print(f"  - {docente.nombreCompleto} asignado a {materias_por_docente} materias de Ciencias Sociales")
                docente_index += 1
        
        # Continuar con las demás materias siguiendo el mismo patrón
        materias_restantes = [
            ("Ciencias Naturales", 6, "Ciencias Naturales"),
            ("Química", 6, "Química"),
            ("Física", 0, "Física"),  # Ya asignados con Matemáticas
            ("Inglés", 4, "Inglés"),
            ("Educación Física", 4, "Educación Física"),
            ("Artes Plásticas", 3, "Artes Plásticas"),
            ("Música", 3, "Música"),
            ("Religión", 3, "Religión")
        ]
        
        for nombre_materia, num_docentes, tipo_materia in materias_restantes:
            if num_docentes == 0:  # Saltar materias ya asignadas
                continue
                
            if nombre_materia in materias_por_tipo:
                materias_tipo = materias_por_tipo[nombre_materia]
                print(f"\nAsignando docentes de {tipo_materia}...")
                
                if len(materias_tipo) > 0 and num_docentes > 0:
                    materias_por_docente = len(materias_tipo) // num_docentes
                    materias_extra = len(materias_tipo) % num_docentes
                    
                    materia_index = 0
                    for i in range(num_docentes):
                        if docente_index >= len(docentes):
                            break
                            
                        docente = docentes[docente_index]
                        
                        # Calcular cuántas materias asignar
                        num_materias_asignar = materias_por_docente
                        if i < materias_extra:
                            num_materias_asignar += 1
                        
                        # Asignar materias
                        for j in range(num_materias_asignar):
                            if materia_index < len(materias_tipo):
                                materia = materias_tipo[materia_index]
                                
                                docente_materia = DocenteMateria(
                                    id=id_counter,
                                    fecha=fecha_asignacion,
                                    docente_ci=docente.ci,
                                    materia_id=materia.id
                                )
                                docente_materias.append(docente_materia)
                                id_counter += 1
                                materia_index += 1
                        
                        if num_materias_asignar > 0:
                            print(f"  - {docente.nombreCompleto} asignado a {num_materias_asignar} materias de {tipo_materia}")
                        docente_index += 1
        
        # Asignar docentes directivos/administrativos a materias restantes si las hay
        materias_sin_asignar = []
        for tipo_materia, lista_materias in materias_por_tipo.items():
            for materia in lista_materias:
                # Verificar si esta materia ya fue asignada
                ya_asignada = any(dm.materia_id == materia.id for dm in docente_materias)
                if not ya_asignada:
                    materias_sin_asignar.append(materia)
        
        if materias_sin_asignar and docente_index < len(docentes):
            print(f"\nAsignando {len(materias_sin_asignar)} materias restantes a directivos...")
            for materia in materias_sin_asignar:
                if docente_index >= len(docentes):
                    break
                    
                docente = docentes[docente_index % len(docentes)]  # Rotar entre docentes restantes
                
                docente_materia = DocenteMateria(
                    id=id_counter,
                    fecha=fecha_asignacion,
                    docente_ci=docente.ci,
                    materia_id=materia.id
                )
                docente_materias.append(docente_materia)
                id_counter += 1
                
                if docente_index < len(docentes) - 4:  # No incrementar si es directivo
                    docente_index += 1
        
        # Guardar todas las asignaciones
        try:
            for docente_materia in docente_materias:
                db.session.add(docente_materia)
            db.session.commit()
            
            print(f"\n✓ Asignaciones DocenteMateria creadas exitosamente: {len(docente_materias)} asignaciones")
            
            # Mostrar estadísticas
            print(f"\nEstadísticas de asignación:")
            print(f"  - Total asignaciones: {len(docente_materias)}")
            print(f"  - Docentes con asignaciones: {len(set(dm.docente_ci for dm in docente_materias))}")
            print(f"  - Materias asignadas: {len(set(dm.materia_id for dm in docente_materias))}")
            
            # Verificar cobertura
            total_materias = len(materias)
            materias_cubiertas = len(set(dm.materia_id for dm in docente_materias))
            print(f"  - Cobertura: {materias_cubiertas}/{total_materias} materias ({(materias_cubiertas/total_materias)*100:.1f}%)")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error al crear asignaciones DocenteMateria: {str(e)}")
def actualizar_nota_final_automatica(estudiante_ci, gestion_id, materia_id):
    """
    Actualiza automáticamente la nota final del estudiante calculando las 4 dimensiones.
    Calcula directamente sin usar imports circulares.
    """
    try:
        # Función local para calcular nota por dimensión (copiada del endpoint)
        def calcular_nota_dimension(dimension_nombre):
            # Buscar la EvaluacionIntegral por nombre
            evaluacion_integral = EvaluacionIntegral.query.filter(
                EvaluacionIntegral.nombre.ilike(dimension_nombre)
            ).first()
            
            if not evaluacion_integral:
                return 0

            # Obtener los tipos de evaluación relacionados a esta dimensión
            tipos_dimension = TipoEvaluacion.query.filter_by(
                evaluacion_integral_id=evaluacion_integral.id
            ).all()
            tipo_ids = [tipo.id for tipo in tipos_dimension]

            if not tipo_ids:
                return 0

            # Buscar todas las evaluaciones del estudiante en esa materia y gestión
            evaluaciones = Evaluacion.query.filter(
                Evaluacion.estudiante_ci == estudiante_ci,
                Evaluacion.materia_id == materia_id,
                Evaluacion.gestion_id == gestion_id,
                Evaluacion.tipo_evaluacion_id.in_(tipo_ids)
            ).all()

            if not evaluaciones:
                return 0

            # Calcular promedio
            suma = sum(eva.nota for eva in evaluaciones)
            promedio = suma / len(evaluaciones)
            return promedio

        # Calcular notas por dimensión
        ser_nota = calcular_nota_dimension("ser")
        hacer_nota = calcular_nota_dimension("hacer")
        saber_nota = calcular_nota_dimension("saber")
        decidir_nota = calcular_nota_dimension("decidir")

        # Calcular promedio final
        promedio = round((ser_nota + hacer_nota + saber_nota + decidir_nota) / 4, 2)

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
                valor=promedio
            )
            db.session.add(nota_final)
        else:
            nota_final.valor = promedio

        return promedio
        
    except Exception as e:
        print(f"Error al actualizar nota final: {str(e)}")
        return 0
