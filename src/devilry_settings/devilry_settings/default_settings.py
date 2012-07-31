
########################################################################
#
# Defaults for django settings
# - See: https://docs.djangoproject.com/en/dev/ref/settings/
#
########################################################################

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
STATIC_ROOT = 'static'
DATABASES = {}
EMAIL_SUBJECT_PREFIX = '[Devilry] '
ROOT_URLCONF = 'devilry_settings.default_root_urlconf'
AUTH_PROFILE_MODULE = 'core.DevilryUserProfile'


INSTALLED_APPS = ['django.contrib.markup',
                  'django.contrib.sessions',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.staticfiles',
                  'django.contrib.sessions',
                  'django.contrib.messages',
                  'django.contrib.admin',
                  'errortemplates',
                  'djangorestframework',
                  'gunicorn',

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
                  'devilry_useradmin',
                  'devilry_settings'
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
DEVILRY_MATHJAX_URL = 'https://d3eoax9i5htok0.cloudfront.net/mathjax/latest/MathJax.js'
DEVILRY_LOGOUT_URL = '/authenticate/logout'
DEVILRY_HELP_URL = 'https://github.com/devilry/devilry-django/wiki'

#Set max file size to 5MB. Files greater than this size are split into chunks of this size.
DEVILRY_MAX_ARCHIVE_CHUNK_SIZE = 5000000

DEVILRY_SEND_EMAIL_TO_USERS = True
DEVILRY_EMAIL_SUBJECT_PREFIX_ADMIN = '[devilry-admin] '
DEVILRY_EMAIL_SIGNATURE = "This is a message from the Devilry assignment delivery system. " \
                  "Please do not respond to this email."

DEVILRY_DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsHierDeliveryStore'
DEVILRY_FSHIERDELIVERYSTORE_INTERVAL = 1000
DEVILRY_SYNCSYSTEM = 'YOUR MASTER SYSTEM HERE'

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


#: Deadline handling method:
#:
#:    0: Soft deadlines
#:    1: Hard deadlines
DEFAULT_DEADLINE_HANDLING_METHOD = 0



#################################################
# Settings without a default value
#################################################

## If we use django to serve static files, we need this setting to define
## where they are located. Static files are located in the devilry/static/
## directory in the devilry source repository.
#DEVILRY_STATIC_ROOT = '/path/to/static'
#DEVILRY_SYSTEM_ADMIN_EMAIL = 'devilry-support@example.com'

