from .develop import *  # noqa
from django_dbdev.backends.postgres import DBSETTINGS


DATABASES = {
    'default': DBSETTINGS
}
DATABASES['default']['PORT'] = 24376
