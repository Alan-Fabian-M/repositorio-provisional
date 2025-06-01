from .tipo_evaluacion_seeder import seed_tipo_evaluacion, seed_evaluacion_integral, seed_materias, seed_cursos, seed_materia_curso, seed_estudiantes, seed_inscripciones_historicas

def run_seeders():
    print("Iniciando proceso de seeding histórico 2024-2025...")
    print("Este proceso creará 600 estudiantes, inscripciones para ambos años,")
    print("y generará automáticamente todas las notas y evaluaciones.\n")
    
    seed_evaluacion_integral()  # Primero las evaluaciones integrales
    seed_tipo_evaluacion()      # Luego los tipos de evaluación
    seed_materias()             # Después las materias específicas por curso
    seed_cursos()               # Luego los cursos (1A-6B)
    seed_materia_curso()        # Enlazamos materias con cursos
    seed_estudiantes()          # Creamos 600 estudiantes
    seed_inscripciones_historicas()  # Inscripciones históricas + gestiones automáticas
    
    print("\n🎉 PROCESO DE SEEDING HISTÓRICO COMPLETADO EXITOSAMENTE 🎉")
    print("Base de datos poblada con datos de gestiones 2024 y 2025")
