"""
ML Routes for Flask API
Provides endpoints for ML predictions and analytics
"""

from flask import Blueprint, jsonify, request
from app.ml.ml_service import ml_service
import logging

logger = logging.getLogger(__name__)

# Create ML blueprint
ml_bp = Blueprint('ml', __name__)

@ml_bp.route('/predict/enrollment', methods=['POST'])
def predict_enrollment():
    """
    Predict enrollment likelihood for a student
    
    POST /ml/predict/enrollment
    {
        "edad": 16
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        edad = data.get('edad', 16)
        
        student_data = {
            'edad': edad
        }
        
        result = ml_service.predict_enrollment_likelihood(student_data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in enrollment prediction endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@ml_bp.route('/recommend/courses', methods=['POST'])
def recommend_courses():
    """
    Recommend courses for a student
    
    POST /ml/recommend/courses
    {
        "edad": 16,
        "turno_preferencia": "Mañana" 
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        edad = data.get('edad', 16)
        turno_preferencia = data.get('turno_preferencia', 'Mañana')
        
        student_data = {
            'edad': edad,
            'turno_preferencia': turno_preferencia
        }
        
        result = ml_service.recommend_courses(student_data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in course recommendation endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@ml_bp.route('/predict/performance', methods=['POST'])
def predict_performance():
    """
    Predict student performance score
    
    POST /ml/predict/performance
    {
        "edad": 16
    }    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        edad = data.get('edad', 16)
        nota_actual = data.get('nota_actual', 70)
        
        from .ml_service_simple import ml_service_simple
        
        student_data = {
            'edad': edad,
            'nota_actual': nota_actual
        }
        
        result = ml_service_simple.predict_performance(student_data)
        
        if not result.get('success', False):
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in performance prediction endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@ml_bp.route('/insights', methods=['GET'])
def get_insights():
    """
    Get system insights and analytics
    
    GET /api/ml/insights
    """
    try:
        # Use the model status function as this is what's available
        result = ml_service.get_model_status()
        
        if result:
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({'error': 'Could not get system insights'}), 500
        
    except Exception as e:
        logger.error(f"Error in insights endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@ml_bp.route('/models/status', methods=['GET'])
def get_models_status():
    """
    Get status of loaded ML models
    
    GET /api/ml/models/status
    """
    try:
        status = {
            'models_loaded': len(ml_service.models),
            'models': {
                'enrollment_prediction': 'enrollment' in ml_service.models,
                'course_recommendation': 'recommendation' in ml_service.models,
                'performance_prediction': 'performance' in ml_service.models
            },
            'scalers_loaded': len(ml_service.scalers),
            'service_ready': len(ml_service.models) > 0
        }
        
        return jsonify({
            'success': True,
            'data': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error in models status endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@ml_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check for ML service
    
    GET /api/ml/health
    """
    try:
        from .ml_service_simple import ml_service_simple
        result = ml_service_simple.get_health_status()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in ML health check: {e}")
        return jsonify({'error': 'Service unhealthy'}), 500

# Error handlers for ML blueprint
@ml_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'ML endpoint not found'}), 404

@ml_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed for this ML endpoint'}), 405

@ml_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal ML service error'}), 500
