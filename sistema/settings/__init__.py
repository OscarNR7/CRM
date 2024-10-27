import os

# Determinar qué configuración usar basado en una variable de entorno
environment = os.environ.get('DJANGO_ENVIRONMENT', 'local')

if environment == 'production':
    from .production import *
else:
    from .local import *