from .test import *  # noqa
from django_dbdev.backends.postgres import DBSETTINGS


DATABASES = {
    'default': DBSETTINGS
}
