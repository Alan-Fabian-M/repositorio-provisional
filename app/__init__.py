from flask import Flask, request, jsonify
from .extensions import db, jwt, ma, api, mi, cors
from .config import Config
from flask_restx import Api
from flask_jwt_extended import JWTManager, verify_jwt_in_request


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    
    # Debug: Verificar configuración cargada
    print("DB URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))

    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    
    # Lista de rutas públicas
    
    
    ma.init_app(app)
    mi.init_app(app, db)
    api.init_app(app)
    cors.init_app(app)
    
    
    
    # Registrar Blueprints (rutas)
    from .routes.Estudiante_Routes import ns as estudiante_ns
    from .routes.Authentication_Routes import ns as authentication_ns
    from .routes.Docente_Routes import ns as docente_ns
    

    api.add_namespace(estudiante_ns)
    api.add_namespace(authentication_ns)
    api.add_namespace(docente_ns)
    
    
    return app