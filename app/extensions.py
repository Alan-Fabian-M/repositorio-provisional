from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restx import Api
from flask_cors import CORS

authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Introduce el JWT con el formato **Bearer &lt;token&gt;**'
    }
}

api = Api(
    title="API de Escuela",
    version="1.0",
    description="API RESTful para la gestión de estudiantes",
    authorizations=authorizations,
    security='Bearer'
)

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
mi = Migrate()
cors = CORS()

