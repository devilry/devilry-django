# Import settings.py
from settings import *

## Alternative log out url. Depends on how you authenticate
#DEVILRY_LOGOUT_URL='/authenticate/logout'

# Authentication against the REMOTE_USER environment variable.
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.RemoteUserBackend'
]
