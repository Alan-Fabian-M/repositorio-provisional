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

# Add the scripts directory to the path to allow importing standalone_data_extractor
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.append(str(script_dir))

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# ML imports
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score

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
            # First check if data exists
            if not (self.data_dir / 'students_data.csv').exists():
                # Need to extract data first
                from standalone_data_extractor import StandaloneDataExtractor
                extractor = StandaloneDataExtractor()
                extractor.extract_all_data()
                logger.info("Data extracted successfully")
            
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
    
    def prepare_enrollment_prediction_data(self):
        """Prepare data for enrollment prediction"""
        logger.info("Preparing enrollment prediction data...")
        
        # Merge students with enrollment counts
        student_features = self.students_df.copy()
        
        # Calculate enrollment rate (binary classification)
        student_features['enrolled'] = (student_features['total_inscripciones'] > 0).astype(int)
        
        # Feature engineering
        student_features['age_group'] = pd.cut(student_features['edad'], 
                                             bins=[0, 14, 16, 18, 100], 
                                             labels=['child', 'teen1', 'teen2', 'adult'])
        
        # Encode categorical variables
        le_age_group = LabelEncoder()
        student_features['age_group_encoded'] = le_age_group.fit_transform(student_features['age_group'].astype(str))
        
        # Features for prediction
        features = ['edad', 'age_group_encoded']
        X = student_features[features]
        y = student_features['enrolled']
        
        self.encoders['age_group'] = le_age_group
        
        return X, y
    
    def prepare_course_recommendation_data(self):
        """Prepare data for course recommendation"""
        logger.info("Preparing course recommendation data...")
        
        # Merge enrollment data with student and course info
        rec_data = self.enrollments_df.merge(self.students_df[['estudiante_id', 'edad']], 
                                           left_on='estudiante_ci', right_on='estudiante_id')
        rec_data = rec_data.merge(self.courses_df[['curso_id', 'nivel', 'turno']], 
                                 on='curso_id')
        
        # Feature engineering
        rec_data['age_group'] = pd.cut(rec_data['edad'], 
                                      bins=[0, 14, 16, 18, 100], 
                                      labels=['child', 'teen1', 'teen2', 'adult'])
        
        # Encode categorical variables
        le_nivel = LabelEncoder()
        le_turno = LabelEncoder()
        le_age_group = LabelEncoder()
        
        rec_data['nivel_encoded'] = le_nivel.fit_transform(rec_data['nivel'].fillna('Primaria').astype(str))
        rec_data['turno_encoded'] = le_turno.fit_transform(rec_data['turno'].fillna('Mañana').astype(str))
        rec_data['age_group_encoded'] = le_age_group.fit_transform(rec_data['age_group'].astype(str))
        
        # Features and target
        features = ['edad', 'age_group_encoded', 'turno_encoded']
        X = rec_data[features]
        y = rec_data['nivel_encoded']
        
        self.encoders['nivel'] = le_nivel
        self.encoders['turno'] = le_turno
        self.encoders['age_group_rec'] = le_age_group
        
        return X, y
    
    def train_enrollment_prediction_model(self):
        """Train enrollment prediction model"""
        logger.info("Training enrollment prediction model...")
        
        X, y = self.prepare_enrollment_prediction_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest model
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = rf_model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Enrollment Prediction Model Accuracy: {accuracy:.4f}")
        
        # Save model and scaler
        self.models['enrollment'] = rf_model
        self.scalers['enrollment'] = scaler
        
        joblib.dump(rf_model, self.models_dir / 'enrollment_prediction_model.pkl')
        joblib.dump(scaler, self.models_dir / 'enrollment_prediction_scaler.pkl')
        
        return rf_model, scaler
    
    def train_course_recommendation_model(self):
        """Train course recommendation model"""
        logger.info("Training course recommendation model...")
        
        X, y = self.prepare_course_recommendation_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest model
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = rf_model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Course Recommendation Model Accuracy: {accuracy:.4f}")
        
        # Save model and scaler
        self.models['course_recommendation'] = rf_model
        self.scalers['course_recommendation'] = scaler
        
        joblib.dump(rf_model, self.models_dir / 'course_recommendation_model.pkl')
        joblib.dump(scaler, self.models_dir / 'course_recommendation_scaler.pkl')
        
        return rf_model, scaler
    
    def train_performance_prediction_model(self):
        """Train performance prediction model (simplified)"""
        logger.info("Training performance prediction model...")
        
        # Create synthetic performance data based on enrollments
        perf_data = self.enrollments_df.merge(self.students_df[['estudiante_id', 'edad']], 
                                            left_on='estudiante_ci', right_on='estudiante_id')
        
        # Simulate performance scores based on age and enrollment patterns
        np.random.seed(42)
        perf_data['performance_score'] = (
            80 + (perf_data['edad'] - 15) * 2 + np.random.normal(0, 10, len(perf_data))
        ).clip(0, 100)
        
        # Features
        features = ['edad']
        X = perf_data[features]
        y = perf_data['performance_score']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Performance Prediction Model - MSE: {mse:.4f}, R2: {r2:.4f}")
        
        # Save model and scaler
        self.models['performance'] = model
        self.scalers['performance'] = scaler
        
        joblib.dump(model, self.models_dir / 'performance_prediction_model.pkl')
        joblib.dump(scaler, self.models_dir / 'performance_prediction_scaler.pkl')
        
        return model, scaler
    
    def save_encoders(self):
        """Save label encoders"""
        logger.info("Saving label encoders...")
        
        for name, encoder in self.encoders.items():
            joblib.dump(encoder, self.models_dir / f'{name}_encoder.pkl')
    
    def train_all_models(self):
        """Train all ML models"""
        logger.info("Starting ML model training pipeline...")
        
        if not self.load_data():
            logger.error("Failed to load data. Exiting.")
            return False
        
        try:
            # Train models
            self.train_enrollment_prediction_model()
            self.train_course_recommendation_model()
            self.train_performance_prediction_model()
            
            # Save encoders
            self.save_encoders()
            
            logger.info("All models trained successfully!")
            
            # Create model summary
            summary = {
                'training_date': datetime.now().isoformat(),
                'models': list(self.models.keys()),
                'data_stats': {
                    'students': len(self.students_df),
                    'courses': len(self.courses_df),
                    'enrollments': len(self.enrollments_df),
                    'teachers': len(self.teachers_df)
                }
            }
            
            import json
            with open(self.models_dir / 'model_summary.json', 'w') as f:
                json.dump(summary, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error during model training: {e}")
            return False

def main():
    """Main function to run ML training"""
    trainer = MLTrainer()
    success = trainer.train_all_models()
      if success:
        print("\n*** ML MODEL TRAINING COMPLETED SUCCESSFULLY! ***")
        print("\nTrained Models:")
        print("- Enrollment Prediction Model")
        print("- Course Recommendation Model") 
        print("- Performance Prediction Model")
        print(f"\nModels saved to: {trainer.models_dir}")
    else:
        print("\n!!! ML Model Training Failed!")

if __name__ == "__main__":
    main()
