# These settings are used when we generate our documentation

from .base import *

MEDIA_ROOT = "filestore"
DATABASES['default']['NAME'] = ':memory:'
