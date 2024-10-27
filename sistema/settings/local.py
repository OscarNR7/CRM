from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-t#tkm%(qvte#l^_v=#s)+*&u$%enigk2zg*yesjprk70%g2g(3'

DEBUG = True
ALLOWED_HOSTS = []

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Logging básico para desarrollo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'error.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'clientes': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'usuarios': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}