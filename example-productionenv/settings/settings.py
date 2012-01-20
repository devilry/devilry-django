from os.path import abspath, dirname, join
from devilry.defaults.settings import *

## Convenience to use paths relative to this file. With the magic below,
## PARENT_DIR is set to the productionenv directory. Some settings below use
## join(PARENT_DIR, 'something') to create OS-independent filesystem paths
## relative to productionenv. Feel free to use absolute paths instead
PARENT_DIR = dirname(dirname(abspath(__file__)))

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+g$%**q(w78xqa_2)(_+%v8d)he-b_^@d*pqhq!#2p*a7*9e9h'

## Where do we store files that students deliver?
# DELIVERY_STORE_ROOT = '/path/to/some/directory'
DELIVERY_STORE_ROOT = join(PARENT_DIR, 'deliverystore')

## You can dump related users into devilry. This setting is where the system
## tells users that this data comes from.
DEVILRY_SYNCSYSTEM = 'FS (Felles Studentsystem)'

## Nice to have this set to True while you are setting up devilry, however set
## it to False for production
DEBUG = True

## Example config for SQLite (see also PostgreSQL below)
DATABASES["default"] = {
    'ENGINE': 'django.db.backends.sqlite3',

    # Path to sqlite database file
    'NAME': join(PARENT_DIR, 'db.sqlite3')
}

## Example config for PostgreSQL
#DATABASES["default"] = {
#    'ENGINE': 'django.db.backends.postgresql_psycopg2',
#    'NAME': 'devilry', # Name of the database
#    'USER': 'devilryuser', # Database user
#    'PASSWORD': 'secret', # Password of database user
#    'HOST': '', # Set to empty string for localhost.
#    'PORT': '', # Set to empty string for default.
#}


#
# Logging
#

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + [
    'devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware',
    #'devilry.utils.profile.ProfilerMiddleware' # Enable profiling. Just add ?prof=yes to any url to see a profile report
]

logdir = join(PARENT_DIR, 'log')
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
                         'mail_admins'],
            'level': 'DEBUG',
            'propagate': False
        },
        'devilry.utils.devilry_email': {
            'handlers': ['allButExceptionTracebacks', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}



#################################
## THESE SETTINGS MUST BE SET
#################################

## The urlscheme+domain where devilry is located.
## DEVILRY_SCHEME_AND_DOMAIN+DEVILRY_URLPATH_PREFIX is the absolute URL to the devilry
## instance. WARNING: must not end with /
#DEVILRY_SCHEME_AND_DOMAIN = 'https://devilry.example.com'

## Email addresses
#DEVILRY_EMAIL_DEFAULT_FROM = 'devilry-support@example.com'
#DEVILRY_SYSTEM_ADMIN_EMAIL = 'devilry-support@example.com'

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.example.com'
#EMAIL_PORT = 25

#DEVILRY_FSHIERDELIVERYSTORE_INTERVAL = None
#DEVILRY_FSHIERDELIVERYSTORE_ROOT = None
