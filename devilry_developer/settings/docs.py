# These settings are used when we generate our documentation

from .base import *

MEDIA_ROOT = "filestore"
DATABASES['default']['NAME'] = ':memory:'
DEVILRY_DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.MemoryDeliveryStore'
HAYSTACK_ENABLE_REGISTRATIONS = False