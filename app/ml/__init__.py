"""
ML Module for Flask API
Machine Learning integration for educational system predictions
"""

from .ml_service import ml_service
from .routes import ml_bp

__all__ = ['ml_service', 'ml_bp']
