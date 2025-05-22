import os
import cloudinary

class CloudinaryConfig:
    CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', 'Si2')
    API_KEY = os.getenv('CLOUDINARY_API_KEY', '441626374645742')
    API_SECRET = os.getenv('CLOUDINARY_API_SECRET', 'qJAFgRUbyHSVc_SitfIXj0ELXFI')
    
    @classmethod
    def init_cloudinary(cls):
        cloudinary.config(
            cloud_name='cls.CLOUD_NAME',
            api_key=cls.API_KEY,
            api_secret=cls.API_SECRET,
            secure=True
        )