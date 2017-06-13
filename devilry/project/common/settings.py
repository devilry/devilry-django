########################################################################
#
# Defaults for django settings
# - See: https://docs.djangoproject.com/en/dev/ref/settings/
#
########################################################################
import os
import devilry


DEBUG = False
EXTJS4_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'Europe/Oslo'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
FORMAT_MODULE_PATH = 'devilry.project.common.formats'
LOGIN_URL = '/authenticate/login'
STATIC_URL = '/static/'
STATIC_ROOT = 'static'
DATABASES = {}
EMAIL_SUBJECT_PREFIX = '[Devilry] '
ROOT_URLCONF = 'devilry.project.production.urls'
AUTH_PROFILE_MODULE = 'core.DevilryUserProfile'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.humanize',
    'errortemplates',
    'errortemplates',
    'crispy_forms',
    'djangorestframework',
    'gunicorn',
    'extjs4',
    'haystack',
    'south',
    # 'djcelery',
    # 'celery_haystack',

    'devilry.devilry_cradmin',
    'django_cradmin',
    'django_cradmin.apps.cradmin_temporaryfileuploadstore',
    'devilry.django_decoupled_docs',

    'devilry.apps.core',
    'devilry.apps.gradeeditors',

    'devilry.devilry_markup',
    'devilry.devilry_superadmin',
    'devilry.devilry_authenticate',
    'devilry.devilry_send_email_to_students',

    'devilry.devilry_help',
    'devilry.devilry_extjsextras',
    'devilry.devilry_theme',
    'devilry.devilry_theme2',
    'devilry.devilry_usersearch',
    'devilry.devilry_authenticateduserinfo',
    'devilry.devilry_header',
    'devilry.devilry_useradmin',
    'devilry.devilry_helplinks',
    'devilry.devilry_frontpage',
    'devilry.devilry_student',
    'devilry.devilry_i18n',
    'devilry.devilry_settings',
    'devilry.devilry_subjectadmin',
    'devilry.devilry_nodeadmin',
    # 'devilry.devilry_search',
    'devilry.devilry_qualifiesforexam',
    'devilry.devilry_qualifiesforexam_approved',
    'devilry.devilry_qualifiesforexam_points',
    'devilry.devilry_qualifiesforexam_select',
    'devilry.devilry_examiner',
    'devilry.devilry_gradingsystem',
    'devilry.devilry_gradingsystemplugin_points',
    'devilry.devilry_gradingsystemplugin_approved',
    'devilry.devilry_rest',
    'devilry.devilry_detektor',
    'devilry.devilry_dumpv2database',
]

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.request",
                               'django.contrib.messages.context_processors.messages',
                               'extjs4.context_processors.extjs4',
                               'devilry.project.common.templatecontext.template_variables')


MIDDLEWARE_CLASSES = ['django.middleware.common.CommonMiddleware',
                      'django.contrib.sessions.middleware.SessionMiddleware',
                      'django.contrib.auth.middleware.AuthenticationMiddleware',
                      'devilry.devilry_i18n.middleware.LocaleMiddleware',
                      'django.contrib.messages.middleware.MessageMiddleware',
                      'devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware']


##################################################################################
#
# Haystack (search)
#
##################################################################################

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'devilry.devilry_search.haystack_signal_processor.DevilryCelerySignalProcessor'


########################################################################
#
# Celery
#
########################################################################
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_EAGER_TRANSACTION = True
CELERY_TIMEZONE = 'Europe/Oslo'
CELERY_ENABLE_UTC = True


########################################################################
#
# Defaults for settings defined by Devilry.
#
########################################################################


# Make sure this does not end with / (i.e. '' means / is the main page).
# DEVILRY_URLPATH_PREFIX = '/django/devilry'
DEVILRY_URLPATH_PREFIX = ''

# The default grade-plugin:
DEVILRY_DEFAULT_GRADEEDITOR = 'approved'

DEVILRY_STATIC_URL = '/static'  # Must not end in / (this means that '' is the server root)
DEVILRY_EXTJS_URL = DEVILRY_STATIC_URL + '/extjs4'
DEVILRY_MATHJAX_URL = 'https://cdn.mathjax.org/mathjax/latest/MathJax.js'
DEVILRY_LOGOUT_URL = '/authenticate/logout'
DEVILRY_HELP_URL = 'https://devilry-userdoc.readthedocs.org'

# Set max file size to 5MB. Files greater than this size are split into chunks of this size.
DEVILRY_MAX_ARCHIVE_CHUNK_SIZE = 5000000

DEVILRY_SEND_EMAIL_TO_USERS = True
DEVILRY_EMAIL_SUBJECT_PREFIX_ADMIN = '[devilry-admin] '
DEVILRY_EMAIL_SIGNATURE = \
    "This is a message from the Devilry assignment delivery system. "\
    "Please do not respond to this email."

DEVILRY_DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsHierDeliveryStore'
DEVILRY_FSHIERDELIVERYSTORE_INTERVAL = 1000
DEVILRY_SYNCSYSTEM = 'YOUR SYNC SYSTEM HERE'
DEVILRY_EMAIL_DEFAULT_FROM = 'devilry-support@example.com'
DEVILRY_SYSTEM_ADMIN_EMAIL = 'devilry-admin@example.com'
DEVILRY_SCHEME_AND_DOMAIN = 'https://devilry.example.com'


#: Email pattern. Set this, and add 'devilry.devilry_autoset_empty_email_by_username' to INSTALLED_APPS
#: to automatically set email to "<username>@DEVILRY_DEFAULT_EMAIL_SUFFIX" if it is not set when a user is saved.
# DEVILRY_DEFAULT_EMAIL_SUFFIX = 'example.com'

#: When sorting by fullname, would you like to sort by last name? Currently
#: only affects the overview over an entire period.
DEVILRY_SORT_FULL_NAME_BY_LASTNAME = True


DEVILRY_QUALIFIESFOREXAM_PLUGINS = [
    'devilry_qualifiesforexam_approved.all',
    'devilry_qualifiesforexam_approved.subset',
    'devilry_qualifiesforexam_points',
    'devilry_qualifiesforexam_select',
]


CRISPY_TEMPLATE_PACK = 'bootstrap3'


#: Deadline handling method:
#:
#:    0: Soft deadlines
#:    1: Hard deadlines
DEFAULT_DEADLINE_HANDLING_METHOD = 0


#: Url where users are directed when they do not have the permissions they believe they should have.
DEVILRY_LACKING_PERMISSIONS_URL = None

#: Url where users are directed when they want to know what to do if their personal info in Devilry is wrong.
DEVILRY_WRONG_USERINFO_URL = None

#: The URL of the official help pages for Devilry.
DEVILRY_OFFICIAL_HELP_URL = 'http://devilry.org#help'

#: Url where users can go to get documentation for Devilry that your organization provides.
DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_URL = None

#: Text for the DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_URL link.
DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_TEXT = None

#: The documentation version to use.
DEVILRY_DOCUMENTATION_VERSION = 'latest'


#: Django apps that override the Devilry javascript translations (which is most
#: of the Devilry user interface).
DEVILRY_JAVASCRIPT_LOCALE_OVERRIDE_APPS = tuple()

#: Default language
LANGUAGE_CODE = 'en'

#: Available languages
gettext_noop = lambda s: s
LANGUAGES = [('en', gettext_noop('English')),
             ('nb', gettext_noop('Norwegian Bokmal'))]


LOCALE_PATHS = [
    os.path.join(
        os.path.abspath(os.path.dirname(devilry.__file__)),
        'locale')
]


#: Enable MathJax?
DEVILRY_ENABLE_MATHJAX = True


###################################################
# Setup logging using the defaults - logs to stderr
###################################################
from devilry.project.log import create_logging_config
LOGGING = create_logging_config()
