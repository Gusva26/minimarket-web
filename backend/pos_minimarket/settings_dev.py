from .settings import *

# Sobreescribir configuraciones para desarrollo
DEBUG = True
ALLOWED_HOSTS = ['*']

# Se elimina el bloque DATABASES de aquí para usar la configuración 
# de MySQL definida en settings.py (que lee del archivo .env)
