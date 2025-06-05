#!/usr/bin/env python3
"""
Data Extractor for ML System
Extracts data from the Flask application database for your school system
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# Add the project root to the path to import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.extensions import db
from app.models.Estudiante_Model import Estudiante
from app.models.Docente_Model import Docente
from app.models.Curso_Model import Curso
from app.models.Inscripcion_Model import Inscripcion
from app import create_app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleDataExtractor:
    def __init__(self):
        self.app = create_app()
        self.output_dir = Path(__file__).parent.parent / 'data'
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_students_data(self):
        """Extract student data for ML analysis"""
        logger.info("Extracting student data...")
        
        with self.app.app_context():
            try:
                # Query students with their enrollments
                students = db.session.query(Estudiante).all()
                
                # Convert to DataFrame
                data = []
                for student in students:
                    # Calculate age if birth date exists
                    age = None
                    if student.fechaNacimiento:
                        age = (datetime.now().date() - student.fechaNacimiento).days // 365
                    
                    # Count enrollments for this student
                    enrollment_count = Inscripcion.query.filter_by(estudiante_ci=student.ci).count()
                    
                    data.append({
                        'estudiante_id': student.ci,
                        'nombre': student.nombreCompleto,
                        'apellido': '',  # Split if needed
                        'email': '',
                        'fecha_nacimiento': student.fechaNacimiento,
                        'telefono': student.telefono,
                        'direccion': '',
                        'apoderado': student.apoderado,
                        'edad': age if age else 18,
                        'total_inscripciones': enrollment_count
                    })
                
                df = pd.DataFrame(data)
                
                # Save to CSV
                output_file = self.output_dir / 'students_data.csv'
                df.to_csv(output_file, index=False, encoding='utf-8')
                logger.info(f"Student data saved to {output_file} ({len(df)} records)")
                
                return df
                
            except Exception as e:
                logger.error(f"Error extracting student data: {e}")
                return pd.DataFrame()
    
    def extract_courses_data(self):
        """Extract course data for ML analysis"""
        logger.info("Extracting course data...")
        
        with self.app.app_context():
            try:
                # Query courses with enrollment counts
                courses = db.session.query(Curso).all()
                
                # Convert to DataFrame
                data = []
                for course in courses:
                    # Count enrollments for this course
                    enrollment_count = Inscripcion.query.filter_by(curso_id=course.id).count()
                    
                    data.append({
                        'curso_id': course.id,
                        'nombre': course.nombre,
                        'descripcion': course.descripcion,
                        'paralelo': course.Paralelo,
                        'turno': course.Turno,
                        'nivel': course.Nivel,
                        'creditos': 0,  # Default value, adjust based on your data
                        'total_inscripciones': enrollment_count
                    })
                
                df = pd.DataFrame(data)
                
                # Save to CSV
                output_file = self.output_dir / 'courses_data.csv'
                df.to_csv(output_file, index=False, encoding='utf-8')
                logger.info(f"Course data saved to {output_file} ({len(df)} records)")
                
                return df
                
            except Exception as e:
                logger.error(f"Error extracting course data: {e}")
                return pd.DataFrame()
    
    def extract_professors_data(self):
        """Extract professor data for ML analysis"""
        logger.info("Extracting professor data...")
        
        with self.app.app_context():
            try:
                # Query professors
                professors = db.session.query(Docente).all()
                
                # Convert to DataFrame
                data = []
                for professor in professors:
                    data.append({
                        'profesor_id': professor.ci,
                        'nombre': professor.nombreCompleto,
                        'apellido': '',  # Split if needed
                        'email': professor.gmail,
                        'telefono': '',
                        'especialidad': 'General',  # Default, adjust based on your data
                        'total_cursos': 0  # Would need to count from course assignments
                    })
                
                df = pd.DataFrame(data)
                
                # Save to CSV
                output_file = self.output_dir / 'professors_data.csv'
                df.to_csv(output_file, index=False, encoding='utf-8')
                logger.info(f"Professor data saved to {output_file} ({len(df)} records)")
                
                return df
                
            except Exception as e:
                logger.error(f"Error extracting professor data: {e}")
                return pd.DataFrame()
    
    def create_analysis_dataset(self):
        """Create a comprehensive dataset for ML analysis"""
        logger.info("Creating comprehensive analysis dataset...")
        
        with self.app.app_context():
            try:
                # Get enrollments with student and course information
                enrollments = db.session.query(
                    Inscripcion.id,
                    Inscripcion.estudiante_ci,
                    Inscripcion.curso_id,
                    Inscripcion.fecha,
                    Inscripcion.descripcion,
                    Estudiante.nombreCompleto.label('estudiante_nombre'),
                    Estudiante.fechaNacimiento,
                    Estudiante.telefono,
                    Estudiante.apoderado,
                    Curso.nombre.label('curso_nombre'),
                    Curso.Paralelo,
                    Curso.Turno,
                    Curso.Nivel
                ).join(
                    Estudiante, Inscripcion.estudiante_ci == Estudiante.ci
                ).join(
                    Curso, Inscripcion.curso_id == Curso.id
                ).all()
                
                # Convert to DataFrame
                data = []
                for enrollment in enrollments:
                    # Calculate age
                    age = 18  # Default
                    if enrollment.fechaNacimiento:
                        age = (datetime.now().date() - enrollment.fechaNacimiento).days // 365
                    
                    data.append({
                        'inscripcion_id': enrollment.id,
                        'estudiante_id': enrollment.estudiante_ci,
                        'curso_id': enrollment.curso_id,
                        'fecha_inscripcion': enrollment.fecha,
                        'estudiante_nombre': enrollment.estudiante_nombre,
                        'curso_nombre': enrollment.curso_nombre,
                        'paralelo': enrollment.Paralelo,
                        'turno': enrollment.Turno,
                        'nivel': enrollment.Nivel,
                        'edad': age,
                        'creditos': 0,  # Default, adjust based on your system
                    })
                
                df = pd.DataFrame(data)
                
                if not df.empty:
                    # Add enrollment count per student
                    enrollment_counts = df.groupby('estudiante_id').size().reset_index(name='total_inscripciones_estudiante')
                    df = df.merge(enrollment_counts, on='estudiante_id', how='left')
                    
                    # Create simple course encoding
                    df['curso_encoded'] = df['curso_id']
                    
                    # Save comprehensive dataset
                    output_file = self.output_dir / 'ml_analysis_dataset.csv'
                    df.to_csv(output_file, index=False, encoding='utf-8')
                    logger.info(f"ML analysis dataset saved to {output_file} ({len(df)} records)")
                
                return df
                
            except Exception as e:
                logger.error(f"Error creating analysis dataset: {e}")
                return pd.DataFrame()
    
    def run_extraction(self):
        """Run complete data extraction process"""
        logger.info("Starting complete data extraction process...")
        
        try:
            # Extract all data
            students_df = self.extract_students_data()
            courses_df = self.extract_courses_data()
            professors_df = self.extract_professors_data()
            analysis_df = self.create_analysis_dataset()
            
            # Create extraction summary
            summary = {
                'extraction_date': datetime.now().isoformat(),
                'students_count': len(students_df),
                'courses_count': len(courses_df),
                'professors_count': len(professors_df),
                'analysis_records': len(analysis_df),
                'status': 'success'
            }
            
            # Save summary
            summary_file = self.output_dir / 'extraction_summary.txt'
            with open(summary_file, 'w', encoding='utf-8') as f:
                for key, value in summary.items():
                    f.write(f"{key}: {value}\n")
            
            logger.info("Data extraction completed successfully!")
            logger.info(f"Summary: {summary}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during data extraction: {e}")
            return False

def main():
    """Main function"""
    extractor = SimpleDataExtractor()
    success = extractor.run_extraction()
    
    if success:
        print("Data extraction completed successfully!")
        return 0
    else:
        print("Data extraction failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
