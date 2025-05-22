from flask import Flask, request, jsonify
from .extensions import db, jwt, ma, api, mi, cors, cloudinary
from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    
    # Debug: Verificar configuración cargada
    print("DB URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))

    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    mi.init_app(app, db)
    api.init_app(app)
    cors.init_app(app)
    
    # Elimina cualquier configuración previa  # Acceso directo a la configuración interna

    # Configuración directa y explícita
    cloudinary.config(
        cloud_name="dozywphod",
        api_key='441626374645742',
        api_secret='qJAFgRUbyHSVc_SitfIXj0ELXFI',
        secure=True
    )

    
    
    # Registrar Blueprints (rutas)
    from .routes.Estudiante_Routes import ns as estudiante_ns
    from .routes.Authentication_Routes import ns as authentication_ns
    from .routes.Docente_Routes import ns as docente_ns
    

    api.add_namespace(estudiante_ns)
    api.add_namespace(authentication_ns)
    api.add_namespace(docente_ns)
    
    
    return app