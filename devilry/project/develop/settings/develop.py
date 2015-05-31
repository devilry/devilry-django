from .base import *

# MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ['devilry.project.develop.middleware.FakeLoginMiddleware']
# HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'


# The if's below is just to make it easy to toggle these settings on and off during development
profiler_middleware = False
if profiler_middleware:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + [
        'devilry.utils.profile.ProfilerMiddleware' # Enable profiling. Just add ?prof=yes to any url to see a profile report
    ]

#DELAY_MIDDLEWARE_TIME = (80, 120) # Wait for randint(*DELAY_MIDDLEWARE_TIME)/100.0 before responding to each request when using DelayMiddleware
#delay_middleware = True
#if delay_middleware:
    #MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + [
        #'devilry.utils.delay_middleware.DelayMiddleware'
    #]



##############################################################
#
# Sentry
#
##############################################################
# RAVEN_CONFIG = {
#     'dsn': 'http://85cc6c611c904a0ebb4afd363fe60fe4:32988134adad4044bc7d13f85f318498@localhost:9000/2',
# }


##################################################################################
# Haystack (search)
##################################################################################
HAYSTACK_CONNECTIONS = {  # Whoosh
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': join(developfilesdir, 'devilry_whoosh_index'),
    },
}

# HAYSTACK_CONNECTIONS = {  # Elastisearch
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://127.0.0.1:9200/',
#         'INDEX_NAME': 'haystack',
#     },
# }



##################################################################################
# Celery
##################################################################################
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_EAGER_TRANSACTION = True

## For testing celery
## - Se the "Developing and testing Celery background tasks" chapter of the developer docs.
# CELERY_ALWAYS_EAGER = False
# BROKER_URL = 'amqp://'
# CELERY_RESULT_BACKEND = 'amqp://'



######################################################
# Email
######################################################

## If you want to test with a "real" smtp server instead of the file backend, see:
##     https://docs.djangoproject.com/en/dev/topics/email/#testing-email-sending
## In short, uncomment the settings below and run the built in smtpd server in python:
##      python -m smtpd -n -c DebuggingServer localhost:1025
## The smtpd server prints emails to stdout.
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'localhost'
#EMAIL_PORT = 1025


# For testing django-celery-email
# INSTALLED_APPS += ['djcelery_email']
# EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
# CELERY_EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
