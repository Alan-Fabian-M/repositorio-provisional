#!/usr/bin/env python3
"""
Script para ejecutar los seeders de la base de datos manualmente.
Uso: python seed_database.py
"""

from app import create_app, db
from app.seeds import run_seeders

def main():
    """Ejecuta los seeders de la base de datos."""
    app = create_app()
    
    with app.app_context():
        print("=== EJECUTANDO SEEDERS DE BASE DE DATOS ===\n")
        
        # Crear todas las tablas si no existen
        db.create_all()
        print("Tablas de base de datos verificadas/creadas.\n")
        
        # Ejecutar seeders
        run_seeders()
        
        print("\n=== PROCESO COMPLETADO ===")

if __name__ == '__main__':
    main()
