# services/cloudinary_service.py
from ..extensions import cloudinary
import cloudinary.uploader

class CloudinaryService:
    @staticmethod
    def upload_image(file):
        """Sube una imagen a Cloudinary y retorna los datos"""
        try:
            upload_result = cloudinary.uploader.upload(file)
            return {
                'url': upload_result.get('secure_url'),
                'public_id': upload_result.get('public_id')
            }
        except Exception as e:
            raise ValueError(f"Error al subir imagen: {str(e)}")

    @staticmethod
    def delete_image(public_id):
        """Elimina una imagen de Cloudinary"""
        try:
            return cloudinary.uploader.destroy(public_id)
        except Exception as e:
            raise ValueError(f"Error al eliminar imagen: {str(e)}")