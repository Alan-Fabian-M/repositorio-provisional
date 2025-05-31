from .tipo_evaluacion_seeder import seed_tipo_evaluacion, seed_evaluacion_integral

def run_seeders():
    print("Iniciando proceso de seeding...")
    seed_evaluacion_integral()  # Primero creamos las evaluaciones integrales
    seed_tipo_evaluacion()      # Luego los tipos de evaluación
    print("Proceso de seeding completado")
