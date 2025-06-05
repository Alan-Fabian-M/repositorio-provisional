"""
ML Integration for Flask API
Provides ML prediction services for the educational system
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.extensions import db
from app.models.Estudiante_Model import Estudiante
from app.models.Curso_Model import Curso
from app.models.Docente_Model import Docente
from app.models.Inscripcion_Model import Inscripcion

# Configure logging
logger = logging.getLogger(__name__)

class MLService:
    """ML Service for educational predictions and recommendations"""
    
        def __init__(self):
        self.models_dir = Path(__file__).parent.parent / 'modelos'
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self._load_models()
    
    def _load_models(self):
        """Load trained ML models and scalers"""
        try:
            # Update models directory path
            self.models_dir = Path(__file__).parent.parent.parent / 'ml_system' / 'modelos'
            
            # Load enrollment prediction model
            enrollment_model_path = self.models_dir / 'enrollment_prediction_model.pkl'
            enrollment_scaler_path = self.models_dir / 'enrollment_prediction_scaler.pkl'
            
            if enrollment_model_path.exists() and enrollment_scaler_path.exists():
                self.models['enrollment'] = joblib.load(enrollment_model_path)
                self.scalers['enrollment'] = joblib.load(enrollment_scaler_path)
                logger.info("Enrollment prediction model loaded successfully")
            
            # Load course recommendation model
            recommendation_model_path = self.models_dir / 'course_recommendation_model.pkl'
            recommendation_scaler_path = self.models_dir / 'course_recommendation_scaler.pkl'
            
            if recommendation_model_path.exists() and recommendation_scaler_path.exists():
                self.models['course_recommendation'] = joblib.load(recommendation_model_path)
                self.scalers['course_recommendation'] = joblib.load(recommendation_scaler_path)
                logger.info("Course recommendation model loaded successfully")
            
            # Load performance prediction model
            performance_model_path = self.models_dir / 'performance_prediction_model.pkl'
            performance_scaler_path = self.models_dir / 'performance_prediction_scaler.pkl'
            
            if performance_model_path.exists() and performance_scaler_path.exists():
                self.models['performance'] = joblib.load(performance_model_path)
                self.scalers['performance'] = joblib.load(performance_scaler_path)
                logger.info("Performance prediction model loaded successfully")
            
            # Load encoders
            for encoder_file in self.models_dir.glob('*_encoder.pkl'):
                encoder_name = encoder_file.stem.replace('_encoder', '')
                self.encoders[encoder_name] = joblib.load(encoder_file)
                logger.info(f"Loaded {encoder_name} encoder")
            
            logger.info(f"ML models loaded from {self.models_dir}")
            
        except Exception as e:
            logger.error(f"Error loading ML models: {e}")
            # Initialize empty models for graceful fallback
            self.models = {}
            self.scalers = {}
            self.encoders = {}
            recommendation_scaler_path = self.models_dir / 'course_recommendation_scaler.pkl'
            
            if recommendation_model_path.exists() and recommendation_scaler_path.exists():
                self.models['recommendation'] = joblib.load(recommendation_model_path)
                self.scalers['recommendation'] = joblib.load(recommendation_scaler_path)
                logger.info("Course recommendation model loaded successfully")
            
            # Load performance prediction model
            performance_model_path = self.models_dir / 'performance_prediction_model.pkl'
            performance_scaler_path = self.models_dir / 'performance_scaler.pkl'
            
            if performance_model_path.exists() and performance_scaler_path.exists():
                self.models['performance'] = joblib.load(performance_model_path)
                self.scalers['performance'] = joblib.load(performance_scaler_path)
                logger.info("Performance prediction model loaded successfully")
            
            logger.info(f"Loaded {len(self.models)} ML models")
            
        except Exception as e:
            logger.error(f"Error loading ML models: {e}")
    
    def predict_enrollment_likelihood(self, student_id: int, course_id: int) -> Dict[str, Any]:
        """Predict likelihood of student enrolling in additional courses"""
        try:
            if 'enrollment' not in self.models:
                return {'error': 'Enrollment prediction model not available'}
            
            # Get student data
            student = Estudiante.query.get(student_id)
            if not student:
                return {'error': 'Student not found'}
            
            # Get course data
            course = Curso.query.get(course_id)
            if not course:
                return {'error': 'Course not found'}
              # Calculate student age
            if student.fechaNacimiento:
                age = (datetime.now().date() - student.fechaNacimiento).days // 365
            else:
                age = 25  # Default age
            
            # Count current enrollments
            enrollment_count = Inscripcion.query.filter_by(estudiante_ci=student.ci).count()
            
            # Prepare features (edad, creditos, curso_encoded)            # For curso_encoded, we'll use course_id as a simple encoding
            features = np.array([[age, 0, course_id]]).astype(float)  # creditos set to 0 as default
            
            # Scale features
            features_scaled = self.scalers['enrollment'].transform(features)
            
            # Make prediction
            prediction_proba = self.models['enrollment'].predict_proba(features_scaled)[0]
            prediction = self.models['enrollment'].predict(features_scaled)[0]
            
            return {
                'student_id': student_id,
                'course_id': course_id,
                'enrollment_likelihood': float(prediction_proba[1]),  # Probability of enrolling
                'prediction': bool(prediction),
                'confidence': float(max(prediction_proba)),
                'current_enrollments': enrollment_count
            }
            
        except Exception as e:
            logger.error(f"Error in enrollment prediction: {e}")
            return {'error': f'Prediction failed: {str(e)}'}
    
    def recommend_courses(self, student_id: int, limit: int = 5) -> Dict[str, Any]:
        """Recommend courses for a student"""
        try:
            if 'recommendation' not in self.models:
                return {'error': 'Course recommendation model not available'}
            
            # Get student data
            student = Estudiante.query.get(student_id)
            if not student:
                return {'error': 'Student not found'}
            
            # Get all courses
            courses = Curso.query.all()
            if not courses:
                return {'error': 'No courses available'}
              # Get courses student is already enrolled in
            enrolled_courses = db.session.query(Inscripcion.curso_id).filter_by(
                estudiante_ci=student_id
            ).subquery()
            
            # Get available courses (not enrolled)
            available_courses = Curso.query.filter(
                ~Curso.id.in_(enrolled_courses)
            ).all()
            
            if not available_courses:
                return {'recommendations': [], 'message': 'Student is enrolled in all available courses'}
            
            # Prepare course features for recommendation
            course_recommendations = []
            
            for course in available_courses[:limit]:
                # Count enrollments for this course
                enrollment_count = Inscripcion.query.filter_by(curso_id=course.id).count()
                  # Prepare features
                features = np.array([[0, enrollment_count]]).astype(float)  # creditos set to 0
                
                # Scale features
                features_scaled = self.scalers['recommendation'].transform(features)
                
                # Get cluster assignment
                cluster = self.models['recommendation'].predict(features_scaled)[0]
                
                # Calculate simple recommendation score
                score = (enrollment_count * 0.7) + ((course.creditos or 0) * 0.3)
                
                course_recommendations.append({
                    'course_id': course.id,
                    'course_name': course.nombre,
                    'description': course.descripcion,
                    'credits': course.creditos,
                    'cluster': int(cluster),
                    'recommendation_score': float(score),
                    'enrollment_count': enrollment_count
                })
            
            # Sort by recommendation score
            course_recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            return {
                'student_id': student_id,
                'recommendations': course_recommendations[:limit],
                'total_available': len(available_courses)
            }
            
        except Exception as e:
            logger.error(f"Error in course recommendation: {e}")
            return {'error': f'Recommendation failed: {str(e)}'}
    
    def predict_student_performance(self, student_id: int) -> Dict[str, Any]:
        """Predict student performance score"""
        try:
            if 'performance' not in self.models:
                return {'error': 'Performance prediction model not available'}
            
            # Get student data
            student = Estudiante.query.get(student_id)
            if not student:
                return {'error': 'Student not found'}
            
            # Calculate student age
            if student.fecha_nacimiento:
                age = (datetime.now().date() - student.fecha_nacimiento).days // 365
            else:
                age = 25  # Default age
            
            # Get student enrollments
            enrollments = Inscripcion.query.filter_by(estudiante_id=student_id).all()
            total_enrollments = len(enrollments)
            
            # Calculate total credits
            total_credits = sum(
                Curso.query.get(enrollment.curso_id).creditos or 0 
                for enrollment in enrollments
            )
            
            # Prepare features (creditos, total_inscripciones_estudiante, edad)
            features = np.array([[total_credits, total_enrollments, age]]).astype(float)
            
            # Scale features
            features_scaled = self.scalers['performance'].transform(features)
            
            # Make prediction
            performance_score = self.models['performance'].predict(features_scaled)[0]
            
            # Classify performance level
            if performance_score >= 80:
                performance_level = 'Excellent'
            elif performance_score >= 70:
                performance_level = 'Good'
            elif performance_score >= 60:
                performance_level = 'Average'
            else:
                performance_level = 'Needs Improvement'
            
            return {
                'student_id': student_id,
                'predicted_score': float(performance_score),
                'performance_level': performance_level,
                'total_credits': total_credits,
                'total_enrollments': total_enrollments,
                'age': age
            }
            
        except Exception as e:
            logger.error(f"Error in performance prediction: {e}")
            return {'error': f'Performance prediction failed: {str(e)}'}
    
    def get_system_insights(self) -> Dict[str, Any]:
        """Get overall system insights and analytics"""
        try:            # Get basic statistics
            total_students = Estudiante.query.count()
            total_courses = Curso.query.count()
            total_professors = Docente.query.count()
            total_enrollments = Inscripcion.query.count()
            
            # Calculate average enrollments per student
            avg_enrollments = total_enrollments / total_students if total_students > 0 else 0
            
            # Get most popular courses
            popular_courses = db.session.query(
                Curso.nombre,
                db.func.count(Inscripcion.id).label('enrollment_count')
            ).join(
                Inscripcion, Curso.id == Inscripcion.curso_id
            ).group_by(
                Curso.id, Curso.nombre
            ).order_by(
                db.func.count(Inscripcion.id).desc()
            ).limit(5).all()
            
            # Get student age distribution
            ages = []
            for student in Estudiante.query.all():
                if student.fecha_nacimiento:
                    age = (datetime.now().date() - student.fecha_nacimiento).days // 365
                    ages.append(age)
            
            age_stats = {
                'average_age': np.mean(ages) if ages else 0,
                'min_age': min(ages) if ages else 0,
                'max_age': max(ages) if ages else 0
            }
            
            return {
                'system_statistics': {
                    'total_students': total_students,
                    'total_courses': total_courses,
                    'total_professors': total_professors,
                    'total_enrollments': total_enrollments,
                    'average_enrollments_per_student': round(avg_enrollments, 2)
                },
                'popular_courses': [
                    {'name': course.nombre, 'enrollments': course.enrollment_count}
                    for course in popular_courses
                ],
                'age_statistics': {
                    'average_age': round(age_stats['average_age'], 1),
                    'min_age': age_stats['min_age'],
                    'max_age': age_stats['max_age']
                },
                'models_status': {
                    'enrollment_model': 'enrollment' in self.models,
                    'recommendation_model': 'recommendation' in self.models,
                    'performance_model': 'performance' in self.models,
                    'total_models_loaded': len(self.models)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system insights: {e}")
            return {'error': f'System insights failed: {str(e)}'}

# Global ML service instance
ml_service = MLService()
