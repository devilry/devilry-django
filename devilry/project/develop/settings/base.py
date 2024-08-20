from os.path import join
from os.path import exists
from devilry.utils import rq_setup

from devilry.project.common.settings import *  # noqa
import dj_database_url

THIS_DIR = os.path.dirname(__file__)

#########################################################
#
# Setup the developfiles/ directory as storage for
# generated files during development
#
#########################################################
developfilesdir = 'devilry_developfiles'
if not exists(developfilesdir):
    os.mkdir(developfilesdir)
logdir = join(developfilesdir, 'log')
if not exists(logdir):
    os.mkdir(logdir)
MEDIA_ROOT = join(developfilesdir, "filestore")

DATABASES = {
    'default': dj_database_url.parse(
        # The default should match postgres in docker-compose.yaml
        os.environ.get('DATABASE_URL', 'postgres://dbdev:dbdev@localhost:23419/dbdev')
    )
}

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    # 'raven.contrib.django.raven_compat', # Sentry client (Raven)
    'devilry.devilry_sandbox',

    'devilry.project.develop',
    #'simple_rest',
    'ievv_opensource.ievvtasks_development',

    # Not apps, but here for the Django test system to discover them:
    'devilry.utils',
]


INTERNAL_IPS = ["127.0.0.1"]
DEBUG = True
STATIC_ROOT = 'static'
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+g$%**q(w78xqa_2)(_+%v8d)he-b_^@d*pqhq!#2p*a7*9e9h'

# If no admins are set, no emails are sent to admins
ADMINS = (
     ('Devilry admin', 'admin@example.com'),
)
MANAGERS = ADMINS
ROOT_URLCONF = 'devilry.project.develop.dev_urls'

DEVILRY_SCHEME_AND_DOMAIN = 'https://devilry.example.com'

DEVILRY_SYNCSYSTEM = 'FS (Felles Studentsystem)'

PASSWORD_HASHERS = (
    #    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
)


# DEVILRY_USERADMIN_USER_READONLY_FIELDS = ['email', 'is_superuser', 'is_staff', 'is_active']
# DEVILRY_USERADMIN_DEVILRYUSERPROFILE_READONLY_FIELDS = ['languagecode', 'full_name']
# DEVILRY_USERADMIN_USER_CHANGE_VIEW_MESSAGE = 'This is a test.'
# DEVILRY_USERADMIN_USER_ADD_VIEW_MESSAGE = 'This is a add test.'
# DEVILRY_USERADMIN_PASSWORD_HELPMESSAGE = 'Passwords are handled by Our Awesome External User Management System. Follow <a href="https://awesome.example.com">this link</a> to reset passwords.'


##################################################################################
# Email
##################################################################################
DEVILRY_SEND_EMAIL_TO_USERS = True
DEVILRY_EMAIL_DEFAULT_FROM = 'devilry-support@example.com'
DEVILRY_SYSTEM_ADMIN_EMAIL = 'devilry-support@example.com'
DEVILRY_DEFAULT_EMAIL_SUFFIX = '@example.com'


#######################################################################
# Logging
#######################################################################

if 'devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.append('devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware')

# MIDDLEWARE += [
#'devilry.utils.profile.ProfilerMiddleware' # Enable profiling. Just add ?prof=yes to any url to see a profile report
# ]


##############################################################
#
# Cache
#
##############################################################
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}


###################################################################################
#
# RQ setup for development
#
###################################################################################

RQ_QUEUES = rq_setup.make_simple_rq_queue_setting()


############################
#
# Model-bakery CUSTOM FIELDS
#
############################

BAKER_CUSTOM_CLASS = 'devilry.project.develop.custom_modelbakery.CustomBaker'

IEVVTASKS_DUMPDATA_DIRECTORY = os.path.join(os.path.dirname(THIS_DIR), 'dumps')

from devilry.project.log import create_logging_config  # noqa
LOGGING = create_logging_config(
    mail_admins=False,
    dangerous_actions_loglevel="DEBUG",
    django_loglevel="DEBUG",
    request_loglevel="DEBUG",
    storages_loglevel="WARNING",  # Set to DEBUG to debug S3 stuff
)
# LOGGING["loggers"]["devilry.devilry_compressionutil.models"] = {
#     'handlers': ['stderr'],
#     'level': "DEBUG",
#     'propagate': False
# }
