# Enable the Celery task queue
import djcelery
djcelery.setup_loader()


########################################################################
#
# Defaults for django settings
# - See: https://docs.djangoproject.com/en/dev/ref/settings/
#
########################################################################

DEBUG = False
EXTJS4_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'Europe/Oslo'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
FORMAT_MODULE_PATH = 'devilry_settings.formats'
LOGIN_URL = '/authenticate/login'
STATIC_URL = '/static/'
STATIC_ROOT = 'static'
DATABASES = {}
EMAIL_SUBJECT_PREFIX = '[Devilry] '
ROOT_URLCONF = 'devilry_settings.default_root_urlconf'
AUTH_PROFILE_MODULE = 'core.DevilryUserProfile'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


INSTALLED_APPS = ['django.contrib.markup',
                  'django.contrib.sessions',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.staticfiles',
                  'django.contrib.sessions',
                  'django.contrib.messages',
                  'django.contrib.admin',
                  'djcelery',
                  'errortemplates',
                  'crispy_forms',
                  'djangorestframework',
                  'gunicorn',
                  'extjs4',
                  'haystack',
                  'south',
                  'celery_haystack',
                  'django_decoupled_docs',

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

                  'devilry_extjsextras',
                  'devilry_theme',
                  'devilry_usersearch',
                  'devilry_authenticateduserinfo',
                  'devilry_header',
                  'devilry_useradmin',
                  'devilry_helplinks',
                  'devilry_frontpage',
                  'devilry_student',
                  'devilry_i18n',
                  'devilry_settings',
                  'devilry_subjectadmin',
                  'devilry_nodeadmin',
                  'devilry_search',
                  'devilry_qualifiesforexam',
                  'devilry_qualifiesforexam_approved',
                  'devilry_qualifiesforexam_points',
                  'devilry_qualifiesforexam_select',
                  'devilry_mathjax',
                  'devilry_examiner',
                  'devilry_gradingsystem',
                  'devilry_gradingsystemplugin_points',
                  'devilry_gradingsystemplugin_approved',
                  'devilry_rest',
                  'devilry_detektor',
                 ]

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.request",
                               'django.contrib.messages.context_processors.messages',
                               'extjs4.context_processors.extjs4',
                               'devilry.apps.theme.templatecontext.template_variables')


MIDDLEWARE_CLASSES = ['django.middleware.common.CommonMiddleware',
                      'django.contrib.sessions.middleware.SessionMiddleware',
                      'django.contrib.auth.middleware.AuthenticationMiddleware',
                      'devilry_i18n.middleware.LocaleMiddleware',
                      'django.middleware.transaction.TransactionMiddleware',
                      'django.contrib.messages.middleware.MessageMiddleware',
                      'devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware']


#######################################################################
#
# Testing
#
#######################################################################

TEST_RUNNER = 'devilry_settings.testsuiterunner.FilterableTestSuiteRunner'
TEST_FILTER = {
    'exclude': [
        'django.*', 'djangorestframework.*',
        'devilry.apps.examiner.tests.simplified.*',
        'devilry.apps.student.tests.simplified.*',
        'devilry.apps.student.tests.simplified.*',
        'devilry_search.tests.*', # Ignored when running all tests because they requir a fullfeatured search backend, like solr, to work
        ],
    'include': ['devilry*']
}

##################################################################################
#
# Haystack (search)
#
##################################################################################
HAYSTACK_SITECONF = 'devilry_search.haystack_search_sites'
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr'


########################################################################
#
# Celery
#
########################################################################
BROKER_URL = 'amqp://devilry:secret@localhost:5672/devilryhost'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'


########################################################################
#
# Defaults for settings defined by Devilry.
#
########################################################################


# Make sure this does not end with / (i.e. '' means / is the main page).
# DEVILRY_URLPATH_PREFIX = '/django/devilry'
DEVILRY_URLPATH_PREFIX = ''

# The default grade-plugin:
DEVILRY_DEFAULT_GRADEEDITOR='approved'

DEVILRY_STATIC_URL = '/static' # Must not end in / (this means that '' is the server root)
DEVILRY_THEME_URL = DEVILRY_STATIC_URL + '/theme/themes/devilry'
DEVILRY_EXTJS_URL = DEVILRY_STATIC_URL + '/extjs4'
DEVILRY_MATHJAX_URL = '{}/devilry_mathjax/MathJax.js'.format(DEVILRY_STATIC_URL)
DEVILRY_LOGOUT_URL = '/authenticate/logout'
DEVILRY_HELP_URL = 'https://devilry-userdoc.readthedocs.org'

#Set max file size to 5MB. Files greater than this size are split into chunks of this size.
DEVILRY_MAX_ARCHIVE_CHUNK_SIZE = 5000000

DEVILRY_SEND_EMAIL_TO_USERS = True
DEVILRY_EMAIL_SUBJECT_PREFIX_ADMIN = '[devilry-admin] '
DEVILRY_EMAIL_SIGNATURE = "This is a message from the Devilry assignment delivery system. " \
                  "Please do not respond to this email."

DEVILRY_DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsHierDeliveryStore'
DEVILRY_FSHIERDELIVERYSTORE_INTERVAL = 1000
DEVILRY_SYNCSYSTEM = 'YOUR SYNC SYSTEM HERE'
DEVILRY_EMAIL_DEFAULT_FROM = 'devilry-support@example.com'
DEVILRY_SYSTEM_ADMIN_EMAIL = 'devilry-admin@example.com'
DEVILRY_SCHEME_AND_DOMAIN = 'https://devilry.example.com'



#: Email pattern. Set this, and add 'devilry.apps.autoset_empty_email_by_username' to INSTALLED_APPS
#: to automatically set email to "<username>@DEVILRY_DEFAULT_EMAIL_SUFFIX" if it is not set when a user is saved.
#DEVILRY_DEFAULT_EMAIL_SUFFIX = 'example.com'

#: When sorting by fullname, would you like to sort by last name? Currently
#: only affects the overview over an entire period.
DEVILRY_SORT_FULL_NAME_BY_LASTNAME = True

#: Messages that are displayed in the 3 dashboards for users with no permission to the dashboard
#: The body of each message can contain html. For example, you can add an email link using: <a href="mailto:admin@example.com">admin@example.com</a>
DEVILRY_STUDENT_NO_PERMISSION_MSG = {'title': 'No published assignments',
                                     'body': 'You are not registered as a student on any assignments in Devilry. This is usually because you subject/course administrator has not published any assignments yet. Contact your subject/course administrator if this is wrong.'}
DEVILRY_EXAMINER_NO_PERMISSION_MSG = {'title': 'You are not an examiner',
                                      'body': 'You are not registered as an examiner on any publshed assignments in Devilry. If this is wrong, please contact the subject/course administrator.'}
DEVILRY_ADMINISTRATOR_NO_PERMISSION_MSG = {'title': 'You are not an administrator',
                                           'body': 'You are not registered as an administrator on any Node, Subject/Course, Period/Semester or Assignment in Devilry. If this is wrong, please contact the system administrator.'}


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


#: Django apps that override the Devilry javascript translations (which is most
#: of the Devilry user interface).
DEVILRY_JAVASCRIPT_LOCALE_OVERRIDE_APPS = tuple()

#: Default language
LANGUAGE_CODE = 'en'

#: Available languages
gettext_noop = lambda s: s
LANGUAGES = [('en', gettext_noop('English')),
             ('nb', gettext_noop('Norwegian Bokmal'))]


#: Enable MathJax?
DEVILRY_ENABLE_MATHJAX = True



###################################################
# Setup logging using the defaults - logs to stderr
###################################################
from devilry_settings.log import create_logging_config
LOGGING = create_logging_config()
