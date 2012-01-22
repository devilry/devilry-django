from os.path import abspath, dirname, join
from devilry.defaults.settings import *

this_dir = dirname(abspath(__file__))

DATABASES = {"default": {
                         'ENGINE': 'django.db.backends.sqlite3',  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                         'NAME': join(this_dir, 'db.sqlite3'),    # Or path to database file if using sqlite3.
                         'USER': '',             # Not used with sqlite3.
                         'PASSWORD': '',         # Not used with sqlite3.
                         'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
                         'PORT': '',             # Set to empty string for default. Not used with sqlite3.
                        }
            }

INSTALLED_APPS += [
                   'devilry.apps.asminimalaspossible_gradeeditor',
                   #'devilry.apps.autoset_empty_email_by_username',
                   #'django_jenkins',
                   #'devilry.apps.gradeform_gradeeditor',
                   #'devilry.projects.dev.apps.test',

                  # Under development
                  'devilry.apps.coredao',
                  'devilry.apps.corerest',
                  'devilry.dataconverter', # Needs to be here since it uses templates

                  'devilry.apps.guibase',
                  'devilry.apps.subjectadmin',

                   # Not apps, but here for the Django test system to discover them:
                   'devilry.utils',
                   'devilry.restful',
                   'devilry.rest',
                   'devilry.simplified',
                   'django_nose']

INTERNAL_IPS = ["127.0.0.1"]
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+g$%**q(w78xqa_2)(_+%v8d)he-b_^@d*pqhq!#2p*a7*9e9h'

# If no admins are set, no emails are sent to admins
ADMINS = (
     ('Devilry admin', 'admin@example.com'),
)
MANAGERS = ADMINS
MEDIA_ROOT = join(this_dir, "filestore")
ROOT_URLCONF = 'devilry.projects.dev.urls'

DEVILRY_SCHEME_AND_DOMAIN = 'https://devilry.example.com'

DEVILRY_DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsHierDeliveryStore'
#DELIVERY_STORE_ROOT = join(this_dir, 'deliverystore')
DEVILRY_FSHIERDELIVERYSTORE_ROOT = join(this_dir, 'deliverystorehier')
DEVILRY_FSHIERDELIVERYSTORE_INTERVAL = 10
DEVILRY_SYNCSYSTEM = 'FS (Felles Studentsystem)'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_PLUGINS = [
    'devilry.apps.developertools.noseplugins.AddSeleniumArgs'
]


##
## Email
##
DEVILRY_SEND_EMAIL_TO_USERS = True
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = join(this_dir, 'email_log')
DEVILRY_EMAIL_DEFAULT_FROM = 'devilry-support@example.com'
DEVILRY_SYSTEM_ADMIN_EMAIL='devilry-support@example.com'
DEVILRY_DEFAULT_EMAIL_SUFFIX='@example.com'

## If you want to test with a "real" smtp server instead of the file backend, see:
##     https://docs.djangoproject.com/en/dev/topics/email/#testing-email-sending
## In short, uncomment the settings below and run the built in smtpd server in python:
##      python -m smtpd -n -c DebuggingServer localhost:1025
## The smtpd server prints emails to stdout.
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'localhost'
#EMAIL_PORT = 1025


#
# The if's below is just to make it easy to toggle these settings on and off during development
#

profiler_middleware = False
if profiler_middleware:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + [
        'devilry.utils.profile.ProfilerMiddleware' # Enable profiling. Just add ?prof=yes to any url to see a profile report
    ]

DELAY_MIDDLEWARE_TIME = (20, 90) # Wait for randint(*DELAY_MIDDLEWARE_TIME)/100.0 before responding to each request when using DelayMiddleware
delay_middleware = False
if delay_middleware:
    MIDDLEWARE_CLASSES = + [
        'devilry.utils.delay_middleware.DelayMiddleware'
    ]



MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ['devilry.apps.developertools.middleware.FakeLoginMiddleware']


#
# Logging
#


MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + [
    'devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware',
    #'devilry.utils.profile.ProfilerMiddleware' # Enable profiling. Just add ?prof=yes to any url to see a profile report
]


logdir = join(this_dir, 'log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s %(asctime)s %(name)s] %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s] %(message)s'
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'simple',
            'class': 'logging.StreamHandler'
        },
        'allButExceptionTracebacks': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class': 'logging.FileHandler',
            'filename': join(logdir, 'all-but-exceptiontracebacks.devilry.log'),
        },
        'dbfile': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class': 'logging.FileHandler',
            'filename': join(logdir, 'db.devilry.log')
        },
        'dbdebugfile': { # Shows the SQL statements
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.FileHandler',
            'filename': join(logdir, 'debug-containing-sqlstatements.db.devilry.log')
        },
        'requestfile': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class': 'logging.FileHandler',
            'filename': join(logdir, 'request.devilry.log')
        },
        'exceptionTracebacksFile': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class': 'logging.FileHandler',
            'filename': join(logdir, 'exception.devilry.log')
        },
        'emailfile': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class': 'logging.FileHandler',
            'filename': join(logdir, 'email.devilry.log')
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True # The traceback email includes an HTML attachment containing the full content of the debug Web page that would have been produced if DEBUG were True. 
        }
    },
    'loggers': {
        'devilry.utils.logexceptionsmiddleware': {
            'handlers': ['exceptionTracebacksFile', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False
        },
        'django.request': {
            'handlers': ['allButExceptionTracebacks',
                         'requestfile', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False
        },
        'django.db.backends': {
            'handlers': ['allButExceptionTracebacks',
                         'dbfile',
                         'dbdebugfile', # Not useful for production since SQL statement logging is disabled when DEBUG=False.
                         'mail_admins'],
            'level': 'DEBUG',
            'propagate': False
        },
        'devilry.utils.devilry_email': {
            'handlers': ['allButExceptionTracebacks', 'console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}
