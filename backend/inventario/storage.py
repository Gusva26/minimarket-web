import io
from PIL import Image
from django.core.files.base import ContentFile
from cloudinary_storage.storage import MediaCloudinaryStorage

class CustomMediaCloudinaryStorage(MediaCloudinaryStorage):
    """
    Storage personalizado de Cloudinary que asegura rewind (.seek(0)) del buffer de archivo
    y comprime imágenes pesadas (>1MB) en servidor a max 800px.
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

        try:
            size = getattr(content, 'size', 0)
            if size > 1 * 1024 * 1024:
                img = Image.open(content)
                img_format = img.format if img.format in ['JPEG', 'PNG', 'WEBP'] else 'JPEG'
                if img.mode in ('RGBA', 'P') and img_format == 'JPEG':
                    img = img.convert('RGB')
                
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format=img_format, quality=82, optimize=True)
                buf.seek(0)
                content = ContentFile(buf.getvalue(), name=name)
        except Exception:
            if hasattr(content, 'seek'):
                try:
                    content.seek(0)
                except Exception:
                    pass

        return super()._upload(name, content)
