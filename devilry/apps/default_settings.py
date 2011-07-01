from devilry_settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'Europe/Oslo'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
DATETIME_FORMAT = "N j, Y, H:i"
LOGIN_URL = '/authenticate/login'

INSTALLED_APPS = ['django.contrib.markup',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',

                  'devilry.apps.core',
                  'devilry.apps.theme',
                  'devilry.apps.extjshelpers',

                  'devilry.apps.student',
                  'devilry.apps.examiner',
                  'devilry.apps.administrator',
                  'devilry.apps.authenticate',

                  # Not apps, but here for django to discover them:
                  'devilry.simplified']

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.debug",
    'devilry.apps.theme.templatecontext.template_variables',
)
