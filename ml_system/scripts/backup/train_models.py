#!/usr/bin/env python3
"""
ML Model Training Script
Trains machine learning models for the educational system
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
import joblib
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# ML imports
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, mean_squared_error, r2_score
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLTrainer:
    def __init__(self):
                self.data_dir = Path(__file__).parent.parent / 'data'
                self.models_dir = Path(__file__).parent.parent / 'modelos'
                self.models_dir.mkdir(exist_ok=True)
                
                self.models = {}
                self.scalers = {}
                self.encoders = {}
        
    def load_data(self):
        """Load data for ML training"""
        logger.info("Loading data for ML training...")
        
        try:
            # First extract data using standalone extractor
            from standalone_data_extractor import StandaloneDataExtractor
            extractor = StandaloneDataExtractor()
            data_results = extractor.extract_all_data()
            
            # Load datasets
            self.students_df = pd.read_csv(self.data_dir / 'students_data.csv')
            self.courses_df = pd.read_csv(self.data_dir / 'courses_data.csv')
            self.enrollments_df = pd.read_csv(self.data_dir / 'enrollments_data.csv')
            self.teachers_df = pd.read_csv(self.data_dir / 'teachers_data.csv')
            
            logger.info(f"Loaded {len(self.students_df)} student records")
            logger.info(f"Loaded {len(self.courses_df)} course records")
            logger.info(f"Loaded {len(self.enrollments_df)} enrollment records")
            logger.info(f"Loaded {len(self.teachers_df)} teacher records")
            
            return True
            
        except FileNotFoundError as e:
            logger.error(f"Data files not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def preprocess_data(self):
        """Preprocess data for ML training"""
        logger.info("Preprocessing data...")
        
        try:
            # Clean and prepare data
            if not self.analysis_df.empty:
                # Remove rows with null student IDs
                self.analysis_df = self.analysis_df.dropna(subset=['estudiante_id'])
                
                # Fill missing values
                self.analysis_df['creditos'] = self.analysis_df['creditos'].fillna(0)
                self.analysis_df['total_inscripciones_estudiante'] = self.analysis_df['total_inscripciones_estudiante'].fillna(0)
                
                # Create age categories
                if 'edad' in self.analysis_df.columns:
                    self.analysis_df['grupo_edad'] = pd.cut(self.analysis_df['edad'], 
                                                           bins=[0, 20, 25, 30, 100], 
                                                           labels=['18-20', '21-25', '26-30', '30+'])
                
                # Encode categorical variables
                if 'curso_nombre' in self.analysis_df.columns:
                    self.course_encoder = LabelEncoder()
                    self.analysis_df['curso_encoded'] = self.course_encoder.fit_transform(
                        self.analysis_df['curso_nombre'].fillna('Unknown')
                    )
                    self.encoders['course_encoder'] = self.course_encoder
                
                logger.info("Data preprocessing completed")
                return True
            else:
                logger.warning("No analysis data available for preprocessing")
                return False
                
        except Exception as e:
            logger.error(f"Error in data preprocessing: {e}")
            return False
    
    def train_enrollment_prediction_model(self):
        """Train model to predict student enrollment patterns"""
        logger.info("Training enrollment prediction model...")
        
        try:
            if self.analysis_df.empty:
                logger.warning("No data available for enrollment prediction")
                return False
            
            # Prepare features for enrollment prediction
            features = []
            if 'edad' in self.analysis_df.columns:
                features.append('edad')
            if 'creditos' in self.analysis_df.columns:
                features.append('creditos')
            if 'curso_encoded' in self.analysis_df.columns:
                features.append('curso_encoded')
            
            if len(features) < 2:
                logger.warning("Insufficient features for enrollment prediction")
                return False
            
            # Create binary target: will student enroll in more courses
            student_enrollments = self.analysis_df.groupby('estudiante_id')['total_inscripciones_estudiante'].first()
            target = (student_enrollments > student_enrollments.median()).astype(int)
            
            # Get features for each student
            student_features = self.analysis_df.groupby('estudiante_id')[features].first()
            
            # Align target and features
            common_students = student_features.index.intersection(target.index)
            X = student_features.loc[common_students]
            y = target.loc[common_students]
            
            if len(X) < 10:
                logger.warning("Insufficient data for training enrollment model")
                return False
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train Random Forest model
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = rf_model.score(X_train_scaled, y_train)
            test_score = rf_model.score(X_test_scaled, y_test)
            
            logger.info(f"Enrollment model - Train accuracy: {train_score:.3f}, Test accuracy: {test_score:.3f}")
            
            # Save model and scaler
            joblib.dump(rf_model, self.models_dir / 'enrollment_prediction_model.pkl')
            joblib.dump(scaler, self.models_dir / 'enrollment_scaler.pkl')
            
            self.models['enrollment'] = rf_model
            self.scalers['enrollment'] = scaler
            
            return True
            
        except Exception as e:
            logger.error(f"Error training enrollment prediction model: {e}")
            return False
    
    def train_course_recommendation_model(self):
        """Train model for course recommendation"""
        logger.info("Training course recommendation model...")
        
        try:
            if self.courses_df.empty:
                logger.warning("No course data available for recommendation")
                return False
            
            # Simple clustering-based recommendation
            features = ['creditos', 'total_inscripciones']
            
            if not all(col in self.courses_df.columns for col in features):
                logger.warning("Missing required columns for course recommendation")
                return False
            
            # Prepare data
            course_features = self.courses_df[features].fillna(0)
            
            if len(course_features) < 3:
                logger.warning("Insufficient courses for recommendation model")
                return False
            
            # Scale features
            scaler = StandardScaler()
            course_features_scaled = scaler.fit_transform(course_features)
            
            # Train clustering model
            n_clusters = min(3, len(course_features))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(course_features_scaled)
            
            # Add clusters to course data
            self.courses_df['cluster'] = clusters
            
            logger.info(f"Course recommendation model trained with {n_clusters} clusters")
            
            # Save model and scaler
            joblib.dump(kmeans, self.models_dir / 'course_recommendation_model.pkl')
            joblib.dump(scaler, self.models_dir / 'course_recommendation_scaler.pkl')
            
            self.models['recommendation'] = kmeans
            self.scalers['recommendation'] = scaler
            
            return True
            
        except Exception as e:
            logger.error(f"Error training course recommendation model: {e}")
            return False
    
    def train_performance_prediction_model(self):
        """Train model to predict student performance"""
        logger.info("Training performance prediction model...")
        
        try:
            if self.analysis_df.empty:
                logger.warning("No data available for performance prediction")
                return False
            
            # Create synthetic performance scores based on available data
            # In a real scenario, you would have actual grades/performance data
            np.random.seed(42)
            student_performance = self.analysis_df.groupby('estudiante_id').agg({
                'creditos': 'sum',
                'total_inscripciones_estudiante': 'first',
                'edad': 'first'
            }).fillna(0)
            
            # Synthetic performance score (for demonstration)
            performance_score = (
                student_performance['creditos'] * 0.4 +
                student_performance['total_inscripciones_estudiante'] * 0.3 +
                (100 - student_performance['edad']) * 0.3 +
                np.random.normal(0, 5, len(student_performance))
            )
            
            # Normalize to 0-100 scale
            performance_score = np.clip(performance_score, 0, 100)
            
            # Prepare features
            features = ['creditos', 'total_inscripciones_estudiante', 'edad']
            X = student_performance[features]
            y = performance_score
            
            if len(X) < 10:
                logger.warning("Insufficient data for performance prediction")
                return False
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train Random Forest Regressor
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = rf_model.score(X_train_scaled, y_train)
            test_score = rf_model.score(X_test_scaled, y_test)
            
            logger.info(f"Performance model - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
            
            # Save model and scaler
            joblib.dump(rf_model, self.models_dir / 'performance_prediction_model.pkl')
            joblib.dump(scaler, self.models_dir / 'performance_scaler.pkl')
            
            self.models['performance'] = rf_model
            self.scalers['performance'] = scaler
            
            return True
            
        except Exception as e:
            logger.error(f"Error training performance prediction model: {e}")
            return False
    
    def create_model_metadata(self):
        """Create metadata file for trained models"""
        logger.info("Creating model metadata...")
        
        try:
            metadata = {
                'training_date': datetime.now().isoformat(),
                'models_trained': list(self.models.keys()),
                'data_summary': {
                    'students_count': len(self.students_df) if hasattr(self, 'students_df') else 0,
                    'courses_count': len(self.courses_df) if hasattr(self, 'courses_df') else 0,
                    'professors_count': len(self.professors_df) if hasattr(self, 'professors_df') else 0
                },
                'model_files': {
                    'enrollment_prediction': 'enrollment_prediction_model.pkl',
                    'course_recommendation': 'course_recommendation_model.pkl',
                    'performance_prediction': 'performance_prediction_model.pkl'
                },
                'scaler_files': {
                    'enrollment_prediction': 'enrollment_scaler.pkl',
                    'course_recommendation': 'course_recommendation_scaler.pkl',
                    'performance_prediction': 'performance_scaler.pkl'
                }
            }
            
            # Save metadata
            metadata_file = self.models_dir / 'model_metadata.txt'
            with open(metadata_file, 'w', encoding='utf-8') as f:
                for key, value in metadata.items():
                    f.write(f"{key}: {value}\n")
            
            logger.info(f"Model metadata saved to {metadata_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating model metadata: {e}")
            return False
    
    def run_training(self):
        """Run complete ML training process"""
        logger.info("Starting ML training process...")
        
        try:
            # Load and preprocess data
            if not self.load_data():
                return False
            
            if not self.preprocess_data():
                return False
            
            # Train models
            models_trained = 0
            
            if self.train_enrollment_prediction_model():
                models_trained += 1
            
            if self.train_course_recommendation_model():
                models_trained += 1
            
            if self.train_performance_prediction_model():
                models_trained += 1
            
            # Create metadata
            self.create_model_metadata()
            
            logger.info(f"ML training completed! {models_trained} models trained successfully.")
            return models_trained > 0
            
        except Exception as e:
            logger.error(f"Error in ML training process: {e}")
            return False

def main():
    """Main function"""
    trainer = MLTrainer()
    success = trainer.run_training()
    
    if success:
        print("ML training completed successfully!")
        return 0
    else:
        print("ML training failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
