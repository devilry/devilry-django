from devilry_settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'Europe/Oslo'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
DATETIME_FORMAT = "N j, Y, H:i"
LOGIN_URL = '/authenticate/login'
STATIC_URL = '/static/'
STATIC_ROOT = 'devilry-static-files'
DATABASES = {}
EMAIL_SUBJECT_PREFIX = '[Devilry] '
ROOT_URLCONF = 'devilry.defaults.root_urlconf'
AUTH_PROFILE_MODULE = 'core.DevilryUserProfile'


INSTALLED_APPS = ['django.contrib.markup',
                  'django.contrib.sessions',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.staticfiles',
                  'django.contrib.sessions',
                  'django.contrib.messages',
                  'django.contrib.admin',
                  'djangorestframework',

                  'devilry.apps.core',
                  'devilry.apps.theme',
                  'devilry.apps.extjshelpers',
                  'devilry.apps.extjsux',
                  'devilry.apps.developertools',
                  'devilry.apps.jsfiledownload',

                  'devilry.apps.approved_gradeeditor',
                  'devilry.apps.manual_gradeeditor',
                  'devilry.apps.autograde_gradeeditor',
                  'devilry.apps.basicform_gradeeditor',
                  'devilry.apps.commentform_gradeeditor',

                  'devilry.apps.statistics',
                  'devilry.apps.markup',
                  'devilry.apps.student',
                  'devilry.apps.examiner',
                  'devilry.apps.administrator',
                  'devilry.apps.superadmin',
                  'devilry.apps.authenticate',
                  'devilry.apps.gradeeditors',
                  'devilry.apps.send_email_to_students',

                  'devilry_usersearch',
                  'devilry_useradmin'
                 ]

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.debug",
                               'django.contrib.messages.context_processors.messages',
                               'devilry.apps.theme.templatecontext.template_variables')


MIDDLEWARE_CLASSES = ['django.middleware.common.CommonMiddleware',
                      'django.contrib.sessions.middleware.SessionMiddleware',
                      'django.contrib.auth.middleware.AuthenticationMiddleware',
                      'django.middleware.transaction.TransactionMiddleware',
                      'django.contrib.messages.middleware.MessageMiddleware',
                      'devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware']
