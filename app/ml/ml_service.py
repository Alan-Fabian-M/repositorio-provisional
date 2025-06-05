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
        self.models_dir = Path(__file__).parent.parent.parent / 'ml_system' / 'modelos'
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self._load_models()
    
    def _load_models(self):
        """Load trained ML models and scalers"""
        try:
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
    
    def predict_enrollment_likelihood(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict the likelihood of a student enrolling
        
        Args:
            student_data: Dictionary containing student information
                - edad: Student age
                
        Returns:
            Dictionary with prediction results
        """
        try:
            if 'enrollment' not in self.models:
                return {
                    'error': 'Enrollment prediction model not available',
                    'success': False
                }
            
            # Prepare features
            edad = student_data.get('edad', 16)
            
            # Create age group
            if edad <= 14:
                age_group_encoded = 0  # child
            elif edad <= 16:
                age_group_encoded = 1  # teen1
            elif edad <= 18:
                age_group_encoded = 2  # teen2
            else:
                age_group_encoded = 3  # adult
            
            # Create feature vector
            features = np.array([[edad, age_group_encoded]])
            
            # Scale features
            features_scaled = self.scalers['enrollment'].transform(features)
            
            # Make prediction
            prediction = self.models['enrollment'].predict(features_scaled)[0]
            probability = self.models['enrollment'].predict_proba(features_scaled)[0]
            
            return {
                'success': True,
                'will_enroll': bool(prediction),
                'enrollment_probability': float(probability[1]),
                'confidence': float(max(probability))
            }
            
        except Exception as e:
            logger.error(f"Error in enrollment prediction: {e}")
            return {
                'error': f'Prediction failed: {str(e)}',
                'success': False
            }
    
    def recommend_courses(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend courses for a student
        
        Args:
            student_data: Dictionary containing student information
                - edad: Student age
                - turno_preferencia: Preferred shift (optional)
                
        Returns:
            Dictionary with course recommendations
        """
        try:
            if 'course_recommendation' not in self.models:
                return {
                    'error': 'Course recommendation model not available',
                    'success': False
                }
            
            # Prepare features
            edad = student_data.get('edad', 16)
            turno_pref = student_data.get('turno_preferencia', 'Mañana')
            
            # Create age group
            if edad <= 14:
                age_group_encoded = 0  # child
            elif edad <= 16:
                age_group_encoded = 1  # teen1
            elif edad <= 18:
                age_group_encoded = 2  # teen2
            else:
                age_group_encoded = 3  # adult
            
            # Encode turno (simplified mapping)
            turno_mapping = {'Mañana': 0, 'Tarde': 1, 'Noche': 2}
            turno_encoded = turno_mapping.get(turno_pref, 0)
            
            # Create feature vector
            features = np.array([[edad, age_group_encoded, turno_encoded]])
            
            # Scale features
            features_scaled = self.scalers['course_recommendation'].transform(features)
            
            # Make prediction
            nivel_prediction = self.models['course_recommendation'].predict(features_scaled)[0]
            
            # Get courses from database
            cursos = Curso.query.all()
            
            # Convert prediction back to nivel name if encoder exists
            if 'nivel' in self.encoders:
                try:
                    nivel_name = self.encoders['nivel'].inverse_transform([nivel_prediction])[0]
                except:
                    nivel_name = "Primaria"
            else:
                nivel_name = "Primaria"
            
            # Filter courses by predicted level
            recommended_courses = []
            for curso in cursos:
                if curso.Nivel and nivel_name.lower() in curso.Nivel.lower():
                    recommended_courses.append({
                        'id': curso.id,
                        'nombre': curso.nombre,
                        'nivel': curso.Nivel,
                        'turno': curso.Turno,
                        'paralelo': curso.Paralelo,
                        'descripcion': curso.descripcion
                    })
            
            return {
                'success': True,
                'recommended_level': nivel_name,
                'courses': recommended_courses[:5],  # Top 5 recommendations
                'total_recommendations': len(recommended_courses)
            }
            
        except Exception as e:
            logger.error(f"Error in course recommendation: {e}")
            return {
                'error': f'Recommendation failed: {str(e)}',
                'success': False
            }
    
    def predict_performance(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict student performance
        
        Args:
            student_data: Dictionary containing student information
                - edad: Student age
                
        Returns:
            Dictionary with performance prediction
        """
        try:
            if 'performance' not in self.models:
                return {
                    'error': 'Performance prediction model not available',
                    'success': False
                }
            
            # Prepare features
            edad = student_data.get('edad', 16)
            
            # Create feature vector
            features = np.array([[edad]])
            
            # Scale features
            features_scaled = self.scalers['performance'].transform(features)
            
            # Make prediction
            performance_score = self.models['performance'].predict(features_scaled)[0]
            
            # Categorize performance
            if performance_score >= 90:
                category = "Excelente"
            elif performance_score >= 80:
                category = "Bueno"
            elif performance_score >= 70:
                category = "Regular"
            else:
                category = "Necesita Mejora"
            
            return {
                'success': True,
                'predicted_score': float(performance_score),
                'performance_category': category,
                'recommendations': self._get_performance_recommendations(performance_score)
            }
            
        except Exception as e:
            logger.error(f"Error in performance prediction: {e}")
            return {
                'error': f'Prediction failed: {str(e)}',
                'success': False
            }
    
    def _get_performance_recommendations(self, score: float) -> List[str]:
        """Get performance improvement recommendations"""
        if score >= 90:
            return [
                "Mantener el excelente rendimiento",
                "Considerar actividades de liderazgo",
                "Participar en proyectos avanzados"
            ]
        elif score >= 80:
            return [
                "Continuar con el buen trabajo",
                "Buscar oportunidades de mejora",
                "Participar en actividades extracurriculares"
            ]
        elif score >= 70:
            return [
                "Reforzar áreas débiles",
                "Buscar apoyo adicional",
                "Establecer metas de mejora"
            ]
        else:
            return [
                "Necesita apoyo urgente",
                "Considerar tutoría especializada",
                "Revisar metodología de estudio"
            ]
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all loaded models"""
        return {
            'models_loaded': list(self.models.keys()),
            'scalers_loaded': list(self.scalers.keys()),
            'encoders_loaded': list(self.encoders.keys()),
            'models_directory': str(self.models_dir),
            'total_models': len(self.models)
        }

# Create global instance
ml_service = MLService()
