# ML System Documentation

## Overview
This ML system provides intelligent predictions and recommendations for the educational platform, including enrollment prediction, course recommendations, and performance forecasting.

## Architecture

### Components
1. **Data Extraction**: `ml_system/scripts/standalone_data_extractor.py`
   - Extracts data directly from PostgreSQL database
   - Generates CSV files for ML training

2. **Model Training**: `ml_system/scripts/train_models_new.py`
   - Trains three ML models using scikit-learn
   - Saves models and scalers for production use

3. **ML Service**: `app/ml/ml_service.py`
   - Loads trained models and provides prediction API
   - Integrates with Flask application

4. **API Endpoints**: `app/ml/routes.py`
   - REST API endpoints for ML predictions
   - JSON input/output format

### Trained Models

#### 1. Enrollment Prediction Model
- **Type**: Random Forest Classifier
- **Purpose**: Predicts likelihood of student enrollment
- **Input Features**: Student age, age group
- **Output**: Enrollment probability and binary prediction
- **Accuracy**: 63.89%

#### 2. Course Recommendation Model  
- **Type**: Random Forest Classifier
- **Purpose**: Recommends appropriate course level for students
- **Input Features**: Student age, age group, preferred shift
- **Output**: Recommended course level and matching courses
- **Accuracy**: 100.00% (note: high accuracy due to clear age-level patterns)

#### 3. Performance Prediction Model
- **Type**: Random Forest Regressor
- **Purpose**: Predicts student academic performance scores
- **Input Features**: Student age
- **Output**: Performance score (0-100) and category
- **Performance**: MSE: 82.25, R²: 0.051

## Data Pipeline

### Extraction Results
- **Students**: 900 records
- **Courses**: 12 records  
- **Enrollments**: 600 records
- **Teachers**: 50 records

### Data Processing
1. Age calculation from birth dates
2. Enrollment counting and aggregation
3. Feature engineering (age groups, categorical encoding)
4. Data validation and cleaning

## API Endpoints

### 1. Enrollment Prediction
```
POST /ml/predict/enrollment
Content-Type: application/json

{
    "edad": 16
}

Response:
{
    "success": true,
    "will_enroll": false,
    "enrollment_probability": 0.41,
    "confidence": 0.59
}
```

### 2. Course Recommendation
```
POST /ml/recommend/courses
Content-Type: application/json

{
    "edad": 16,
    "turno_preferencia": "Mañana"
}

Response:
{
    "success": true,
    "recommended_level": "Primaria",
    "courses": [...],
    "total_recommendations": 5
}
```

### 3. Performance Prediction
```
POST /ml/predict/performance
Content-Type: application/json

{
    "edad": 16
}

Response:
{
    "success": true,
    "predicted_score": 81.32,
    "performance_category": "Bueno",
    "recommendations": [...]
}
```

### 4. Model Status
```
GET /ml/status

Response:
{
    "models_loaded": ["enrollment", "course_recommendation", "performance"],
    "scalers_loaded": ["enrollment", "course_recommendation", "performance"],
    "encoders_loaded": ["age_group", "nivel", "turno"],
    "models_directory": "...",
    "total_models": 3
}
```

## Installation and Setup

### 1. Install Dependencies
```bash
pip install pandas numpy scikit-learn matplotlib seaborn joblib psycopg2-binary
```

### 2. Extract Data
```bash
cd ml_system/scripts
python standalone_data_extractor.py
```

### 3. Train Models
```bash
cd ml_system/scripts  
python train_models_new.py
```

### 4. Start Flask Application
```bash
python run.py
```

## File Structure
```
ml_system/
├── setup_ml.py              # Main setup script
├── data/                     # Data storage
│   ├── students_data.csv
│   ├── courses_data.csv
│   ├── enrollments_data.csv
│   ├── teachers_data.csv
│   └── extraction_summary.csv
├── modelos/                  # Trained models
│   ├── enrollment_prediction_model.pkl
│   ├── course_recommendation_model.pkl
│   ├── performance_prediction_model.pkl
│   ├── *_scaler.pkl         # Feature scalers
│   ├── *_encoder.pkl        # Label encoders
│   └── model_summary.json
├── scripts/                  # Training scripts
│   ├── standalone_data_extractor.py
│   └── train_models_new.py
├── docs/                     # Documentation
└── tests/                    # Unit tests

app/ml/                      # Flask integration
├── __init__.py
├── ml_service.py           # ML service class
├── routes.py               # API endpoints
└── prediction_service.py   # Additional services
```

## Model Performance

### Training Data Statistics
- **Training Date**: 2025-06-03
- **Total Students**: 900
- **Total Courses**: 12
- **Total Enrollments**: 600
- **Total Teachers**: 50

### Model Metrics
1. **Enrollment Prediction**: 63.89% accuracy
2. **Course Recommendation**: 100% accuracy
3. **Performance Prediction**: R² = 0.051, MSE = 82.25

## Future Improvements

### Data Enhancements
1. Add more student demographic features
2. Include historical grade data
3. Incorporate course difficulty ratings
4. Add teacher performance metrics

### Model Improvements
1. Implement ensemble methods
2. Add deep learning models
3. Include time series analysis
4. Implement collaborative filtering

### Feature Engineering
1. Create interaction features
2. Add temporal features
3. Include geographic data
4. Implement text analysis on course descriptions

## Troubleshooting

### Common Issues
1. **Database Connection**: Ensure PostgreSQL credentials are correct
2. **Missing Models**: Run training script before using ML service
3. **Flask Context**: ML service requires application context for database queries
4. **Feature Warnings**: Normal sklearn warnings about feature names

### Logs Location
- Training logs: Console output during model training
- Service logs: Flask application logs
- Error logs: Check Flask error logs for ML service issues

## Maintenance

### Regular Tasks
1. Retrain models monthly with new data
2. Monitor prediction accuracy
3. Update feature engineering as needed
4. Backup trained models

### Model Updates
1. Extract fresh data using `standalone_data_extractor.py`
2. Retrain models using `train_models_new.py`
3. Restart Flask application to load new models
4. Test endpoints to verify functionality
