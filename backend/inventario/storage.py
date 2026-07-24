from cloudinary_storage.storage import MediaCloudinaryStorage

class CustomMediaCloudinaryStorage(MediaCloudinaryStorage):
    """
    Storage personalizado de Cloudinary que asegura rewind (.seek(0)) del buffer de archivo.
    Previene el error 'cloudinary.exceptions.BadRequest: Empty file' al subir desde DRF.
    """
    def _upload(self, name, content):
        if hasattr(content, 'seek'):
            try:
                content.seek(0)
            except Exception:
                pass
        if hasattr(content, 'file') and hasattr(content.file, 'seek'):
            try:
                content.file.seek(0)
            except Exception:
                pass
        return super()._upload(name, content)
