#!/usr/bin/env python3
"""
Standalone Data Extractor for ML System
Extracts data directly from the database without Flask app context
"""

import os
import sys
import pandas as pd
import psycopg2
from pathlib import Path
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StandaloneDataExtractor:
    def __init__(self, db_uri=None):
        if db_uri is None:
            # Use the same database URI as the Flask app
            db_uri = 'postgresql://escuela_8lcq_user:kpuXPA7k4xYFmTNQqBIeW8tQmg1wgzBc@dpg-d0uqvbeuk2gs739bo2ng-a.oregon-postgres.render.com/escuela_8lcq'
        
        self.db_uri = db_uri
        self.output_dir = Path(__file__).parent.parent / 'data'
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Using PostgreSQL database")
        
    def get_connection(self):
        """Create database connection"""
        try:
            return psycopg2.connect(self.db_uri)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return None
    
    def extract_students_data(self):
        """Extract student data for ML analysis"""
        logger.info("Extracting student data...")
        
        conn = self.get_connection()
        if not conn:
            return pd.DataFrame()
        
        try:            # SQL query for students data
            query = """
            SELECT 
                e.ci as estudiante_id,
                e."nombreCompleto" as nombre,
                e."fechaNacimiento",
                e.telefono,
                e.apoderado,
                COUNT(i.id) as total_inscripciones
            FROM estudiante e
            LEFT JOIN inscripcion i ON e.ci = i.estudiante_ci
            GROUP BY e.ci, e."nombreCompleto", e."fechaNacimiento", e.telefono, e.apoderado
            """
            
            df = pd.read_sql_query(query, conn)
              # Calculate age
            if 'fechaNacimiento' in df.columns:
                df['fechaNacimiento'] = pd.to_datetime(df['fechaNacimiento'], errors='coerce')
                df['edad'] = df['fechaNacimiento'].apply(
                    lambda x: (datetime.now().date() - x.date()).days // 365 
                    if pd.notna(x) else 18
                )
            else:
                df['edad'] = 18
            
            # Save to CSV
            output_file = self.output_dir / 'students_data.csv'
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Student data saved to {output_file} ({len(df)} records)")
            
            return df
            
        except Exception as e:
            logger.error(f"Error extracting student data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def extract_courses_data(self):
        """Extract course data for ML analysis"""
        logger.info("Extracting course data...")
        
        conn = self.get_connection()
        if not conn:
            return pd.DataFrame()
        
        try:            # SQL query for courses data
            query = """
            SELECT 
                c.id as curso_id,
                c.nombre,
                c.descripcion,
                c."Paralelo" as paralelo,
                c."Turno" as turno,
                c."Nivel" as nivel,
                COUNT(i.id) as total_inscripciones
            FROM curso c
            LEFT JOIN inscripcion i ON c.id = i.curso_id
            GROUP BY c.id, c.nombre, c.descripcion, c."Paralelo", c."Turno", c."Nivel"
            """
            
            df = pd.read_sql_query(query, conn)
            
            # Save to CSV
            output_file = self.output_dir / 'courses_data.csv'
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Course data saved to {output_file} ({len(df)} records)")
            
            return df
            
        except Exception as e:
            logger.error(f"Error extracting course data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def extract_enrollments_data(self):
        """Extract enrollment data for ML analysis"""
        logger.info("Extracting enrollment data...")
        
        conn = self.get_connection()
        if not conn:
            return pd.DataFrame()
        
        try:            # SQL query for enrollments data
            query = """
            SELECT 
                i.id as inscripcion_id,
                i.estudiante_ci,
                i.curso_id,
                i.fecha,
                i.descripcion as estado,
                e."nombreCompleto" as estudiante_nombre,
                c.nombre as curso_nombre,
                c."Nivel" as curso_nivel,
                c."Paralelo" as curso_paralelo,
                c."Turno" as curso_turno
            FROM inscripcion i
            JOIN estudiante e ON i.estudiante_ci = e.ci
            JOIN curso c ON i.curso_id = c.id
            """
            
            df = pd.read_sql_query(query, conn)
              # Process dates
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                df['mes_inscripcion'] = df['fecha'].dt.month
                df['año_inscripcion'] = df['fecha'].dt.year
            
            # Save to CSV
            output_file = self.output_dir / 'enrollments_data.csv'
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Enrollment data saved to {output_file} ({len(df)} records)")
            
            return df
            
        except Exception as e:
            logger.error(f"Error extracting enrollment data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def extract_teachers_data(self):
        """Extract teacher data for ML analysis"""
        logger.info("Extracting teacher data...")
        
        conn = self.get_connection()
        if not conn:
            return pd.DataFrame()
        
        try:            # SQL query for teachers data
            query = """
            SELECT 
                d.ci as docente_ci,
                d."nombreCompleto" as nombre,
                d.gmail as email,
                d."esDocente",
                COUNT(dm.id) as total_materias
            FROM docente d
            LEFT JOIN docente_materia dm ON d.ci = dm.docente_ci
            GROUP BY d.ci, d."nombreCompleto", d.gmail, d."esDocente"
            """
            
            df = pd.read_sql_query(query, conn)
            
            # Save to CSV
            output_file = self.output_dir / 'teachers_data.csv'
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Teacher data saved to {output_file} ({len(df)} records)")
            
            return df
            
        except Exception as e:
            logger.error(f"Error extracting teacher data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def extract_all_data(self):
        """Extract all data for ML analysis"""
        logger.info("Starting complete data extraction...")
        
        results = {
            'students': self.extract_students_data(),
            'courses': self.extract_courses_data(),
            'enrollments': self.extract_enrollments_data(),
            'teachers': self.extract_teachers_data()
        }
        
        # Create a summary report
        summary = []
        for name, df in results.items():
            summary.append({
                'dataset': name,
                'records': len(df),
                'columns': list(df.columns) if not df.empty else [],
                'extracted': not df.empty
            })
        
        summary_df = pd.DataFrame(summary)
        summary_file = self.output_dir / 'extraction_summary.csv'
        summary_df.to_csv(summary_file, index=False)
        
        logger.info("Data extraction completed!")
        logger.info(f"Summary saved to {summary_file}")
        
        return results

def main():
    """Main function to run data extraction"""
    extractor = StandaloneDataExtractor()
    results = extractor.extract_all_data()
    
    print("\n=== DATA EXTRACTION SUMMARY ===")
    for name, df in results.items():
        print(f"{name.capitalize()}: {len(df)} records")
        if not df.empty:
            print(f"  Columns: {', '.join(df.columns)}")
        print()

if __name__ == "__main__":
    main()
