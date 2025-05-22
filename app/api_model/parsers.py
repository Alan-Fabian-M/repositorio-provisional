from flask_restx import reqparse
from werkzeug.datastructures import FileStorage

# Parser para upload de imágenes
upload_parser = reqparse.RequestParser()
upload_parser.add_argument(
    'file', 
    type=FileStorage,  # Usa FileStorage directamente
    location='files',
    required=True,
    help='Imagen del estudiante (JPEG/PNG)'
)

estudiante_parser = reqparse.RequestParser()
estudiante_parser.add_argument('nombreCompleto', required=True, help="Nombre completo requerido")
estudiante_parser.add_argument('ci', type=int, required=True, help="CI numérico requerido")
estudiante_parser.add_argument('fechaNacimiento', required=True, help="Formato YYYY-MM-DD")
estudiante_parser.add_argument('apoderado', required=False)
estudiante_parser.add_argument('telefono', required=False)
estudiante_parser.add_argument('file', type=FileStorage, location='files', required=False)