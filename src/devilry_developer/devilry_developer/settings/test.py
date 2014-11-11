from .base import *

# Disable haystack (speeds up tests a lot)
HAYSTACK_SEARCH_ENGINE = 'dummy' # http://django-haystack.readthedocs.org/en/v1.2.7/tutorial.html#modify-your-settings-py
HAYSTACK_SITECONF = 'devilry_developer.dummy_haystack_search_sites'

SOUTH_TESTS_MIGRATE = False # To disable migrations and use syncdb instead
SKIP_SOUTH_TESTS = True # To disable South's own unit tests

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'

if 'devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware' in MIDDLEWARE_CLASSES:
    MIDDLEWARE_CLASSES.remove('devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware')
