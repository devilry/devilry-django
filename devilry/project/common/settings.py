########################################################################
#
# Defaults for django settings
# - See: https://docs.djangoproject.com/en/dev/ref/settings/
#
########################################################################
import os
import devilry

from .projectspecific_settings import *  # noqa
from .cradmin_legacy_settings import *  # noqa

DEBUG = False

TIME_ZONE = 'Europe/Oslo'
SITE_ID = 1  # Warning: required by django allauth
USE_I18N = True
USE_L10N = True
USE_TZ = True
FORMAT_MODULE_PATH = 'devilry.project.common.formats'
# LOGIN_URL = '/authenticate/login'
LOGIN_URL = '/authenticate/allauth/login/'
STATIC_URL = '/static/'
STATIC_ROOT = 'static'
DATABASES = {}
EMAIL_SUBJECT_PREFIX = '[Devilry] '
ROOT_URLCONF = 'devilry.project.production.urls'
DEFAULT_FROM_EMAIL = 'devilry-support@example.com'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
TEST_RUNNER = 'devilry.project.common.devilry_test_runner.DevilryTestRunner'
AUTH_USER_MODEL = 'devilry_account.User'
LOGIN_REDIRECT_URL = '/'
CRISPY_TEMPLATE_PACK = 'bootstrap3'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.forms',
    'django.contrib.sites',  # Required by django-allauth
    'crispy_forms',
    'gunicorn',
    'ievv_opensource.ievvtasks_common',
    'ievv_opensource.ievv_batchframework',
    'ievv_opensource.ievv_customsql',
    'ievv_opensource.ievv_developemail',
    'django_rq',
    'rest_framework',
    'devilry.devilry_bulkcreate_users',
    'devilry.devilry_cradmin',
    'cradmin_legacy',
    'cradmin_legacy.apps.cradmin_temporaryfileuploadstore',
    'devilry.django_decoupled_docs',

    'cradmin_legacy.apps.cradmin_authenticate',
    'devilry.devilry_resetpassword',
    'cradmin_legacy.apps.cradmin_resetpassword',
    'django_cradmin.apps.cradmin_generic_token_with_metadata',

    'devilry.apps.core.apps.CoreAppConfig',

    'devilry.devilry_account.apps.AccountAppConfig',
    'devilry.devilry_markup',
    'devilry.devilry_superadmin',
    'devilry.devilry_authenticate',

    'devilry.devilry_errortemplates',
    'devilry.devilry_help',
    'devilry.devilry_theme3',
    'devilry.devilry_header',
    'devilry.devilry_frontpage',
    'devilry.devilry_student',
    'devilry.devilry_compressionutil',
    'devilry.devilry_group',
    'devilry.devilry_gradeform',
    'devilry.devilry_comment',
    'devilry.devilry_email',
    'devilry.devilry_i18n',
    'devilry.devilry_settings',
    'devilry.devilry_qualifiesforexam',
    'devilry.devilry_qualifiesforexam_plugin_approved',
    'devilry.devilry_qualifiesforexam_plugin_points',
    'devilry.devilry_qualifiesforexam_plugin_students',
    # 'devilry.devilry_qualifiesforexam_approved',
    # 'devilry.devilry_qualifiesforexam_points',
    # 'devilry.devilry_qualifiesforexam_select',
    'devilry.devilry_examiner',
    'devilry.devilry_gradingsystem',
    'devilry.devilry_gradingsystemplugin_points.apps.GradingsystemPointsAppConfig',
    'devilry.devilry_gradingsystemplugin_approved.apps.GradingsystemApprovedAppConfig',
    #'devilry.devilry_rest',
    'devilry.devilry_admin',
    'devilry.devilry_dbcache',
    'devilry.devilry_deadlinemanagement',
    'devilry.project.common',
    'devilry.devilry_import_v2database',
    #'devilry.devilry_detektor',
    'devilry.devilry_statistics',
    'devilry.devilry_message',
    'devilry.devilry_report',

    # Django-allauth for dataporten login
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'cradmin_legacy.context_processors.cradmin',
                'devilry.project.common.templatecontext.template_variables',
            ],
        },
    },
]


MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'devilry.devilry_i18n.middleware.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware',
    'devilry.devilry_account.middleware.LocalMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

##################################################################################
# Django Cradmin settings (Auth backend, forgotten password and sitename)
##################################################################################
AUTHENTICATION_BACKENDS = [
    'devilry.devilry_account.authbackend.default.EmailAuthBackend',
]


# ievv_batchframework task mode.
IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS = False


########################################################################
#
# i18n
#
########################################################################

#: Default language
LANGUAGE_CODE = 'en'

#: Available languages
gettext_noop = lambda s: s
LANGUAGES = [('en', gettext_noop('English')),
             ('nb', gettext_noop('Norwegian Bokmal'))]

CRADMIN_LEGACY_MOMENTJS_LOCALE = None


LOCALE_PATHS = [
    os.path.join(
        os.path.abspath(os.path.dirname(devilry.__file__)),
        'locale')
]

###############################
#
# RQ
#
###############################
RQ_QUEUES = {}

###################################################
# Setup logging using the defaults - logs to stderr
###################################################
from devilry.project.log import create_logging_config
LOGGING = create_logging_config()



###################################################
# Django allauth settings
###################################################
SOCIALACCOUNT_ADAPTER = 'devilry.devilry_authenticate.allauth_adapter.DevilrySocialAccountAdapter'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'shortname'
ACCOUNT_AUTHENTICATION_METHOD = 'username'

DATAPORTEN_LOGOUT_URL = 'https://auth.dataporten.no/logout'

# Bypasses built-in support for signup.
SOCIALACCOUNT_LOGIN_ON_GET = True



###################################################
# HTML sanitizer settings
###################################################
from html_sanitizer.sanitizer import sanitize_href, tag_replacer, target_blank_noopener, bold_span_to_strong, italic_span_to_em
HTML_SANITIZERS = {
    'devilry': {
        "tags": {
            "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
            "li", "br", "sub", "sup", "hr", "img", "code", "pre", "div",
            "span", "devilry-latex-math", "script"
        },
        "attributes": {
            "a": ("href", "name", "target", "title", "id", "rel",),
            "img": ("src", "alt", "title"),
            "code": ("class",),
            "div": ("class",),
            "devilry-latex-math": ("data-latex-code", "data-variant"),
            "span": ("class",),
        },
        "empty": {"hr", "a", "br", "img", "span", "devilry-latex-math"},
        "separate": {"a", "p", "li"},
        "whitespace": {"br"},
        "keep_typographic_whitespace": True,
        "add_nofollow": False,
        "autolink": False,
        "sanitize_href": sanitize_href,
        "element_preprocessors": [
            # convert span elements into em/strong if a matching style rule
            # has been found. strong has precedence, strong & em at the same
            # time is not supported
            bold_span_to_strong,
            italic_span_to_em,
            tag_replacer("b", "strong"),
            tag_replacer("i", "em"),
            tag_replacer("form", "p"),
            target_blank_noopener,
        ],
        "element_postprocessors": [],
        "is_mergeable": lambda e1, e2: False,
    }
}
