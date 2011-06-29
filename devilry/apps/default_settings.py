from devilry_settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'Europe/Oslo'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/media/'
DATETIME_FORMAT = "N j, Y, H:i"
LOGIN_URL = '/ui/login'

INSTALLED_APPS = [
    'django.contrib.markup',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.webdesign',
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'devilry.apps.core',
    'devilry.apps.ui',
    'devilry.apps.theme',
    'devilry.apps.extjshelpers',

    'devilry.apps.student',
    'devilry.apps.examiner',
    'devilry.apps.administrator',
    'devilry.apps.grade_approved',
    'devilry.apps.grade_default',
    'devilry.apps.grade_rstschema',
    'devilry.apps.quickdash',
    'devilry.apps.gradestats',

    # Not apps, but here for django to discover them:
    'devilry.simplified'
]

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.debug",
    'devilry.apps.ui.templatecontext.template_variables',
)
