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



#INSTALLED_APPS = (
    #'django.contrib.markup', 
    #'django.contrib.sessions',
    #'django.contrib.sites',
    #'django.contrib.admin',
    #'django.contrib.webdesign',
    #'django.contrib.auth',
    #'django.contrib.contenttypes',

    #'devilry.apps.core',
    #'devilry.apps.ui',
    #'devilry.apps.gui',
    #'devilry.apps.xmlrpc',

    #'devilry.apps.simplified',
    #'devilry.apps.restful',

    #'devilry.apps.student',
    #'devilry.apps.examiner',
    #'devilry.apps.xmlrpc_examiner',
    #'devilry.apps.admin',
    #'devilry.apps.grade_approved',
    #'devilry.apps.grade_default',
    #'devilry.apps.grade_schema',
    #'devilry.apps.grade_rstschema',
    #'devilry.apps.quickdash',
    #'devilry.apps.gradestats',

    #'devilry.apps.xmlrpc_client',
    #'devilry.apps.guiexamples',
#)


INSTALLED_APPS = (
    'django.contrib.markup', 
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'devilry.apps.student',
    'devilry.apps.examiner',
    'devilry.apps.admin',
    'devilry.apps.grade_approved',
    'devilry.apps.grade_default',
    'devilry.apps.grade_schema',
    'devilry.apps.grade_rstschema',
    'devilry.apps.quickdash',
    'devilry.apps.xmlrpc_examiner',
    'devilry.apps.xmlrpc',
    'devilry.apps.xmlrpc_client',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'devilry.apps.core',
    'devilry.apps.ui',
    'devilry.apps.adminscripts',
    'devilry.apps.gradestats',

    'devilry.apps.gui',
    'devilry.apps.guiexamples',
    'devilry.apps.simplified',
    'devilry.apps.restful',
    'django.contrib.webdesign',
)




TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.debug",
    'devilry.apps.core.templatecontext.template_variables',
)
