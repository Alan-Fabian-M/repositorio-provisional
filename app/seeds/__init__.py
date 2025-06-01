from .tipo_evaluacion_seeder import seed_tipo_evaluacion, seed_evaluacion_integral, seed_materias, seed_cursos, seed_materia_curso, seed_estudiantes, seed_inscripciones

def run_seeders():
    print("Iniciando proceso de seeding...")
    seed_materias()             # Primero creamos las materias
    seed_cursos()               # Luego creamos los cursos
    seed_materia_curso()        # Después enlazamos materias con cursos
    seed_estudiantes()          # Creamos los estudiantes
    seed_inscripciones()        # Inscribimos estudiantes en cursos
    seed_evaluacion_integral()  # Después creamos las evaluaciones integrales
    seed_tipo_evaluacion()      # Finalmente los tipos de evaluación
    print("Proceso de seeding completado")
