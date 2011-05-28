# Django settings for devilry project.
from os.path import abspath, dirname, join

this_dir = dirname(abspath(__file__))


INTERNAL_IPS = ["127.0.0.1"]
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# If no admins are set, no emails are sent to admins
ADMINS = (
     #('Devilry admin', 'admin@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.sqlite3',  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': join(this_dir, 'db.sqlite3'),    # Or path to database file if using sqlite3.
        'USER': '',             # Not used with sqlite3.
        'PASSWORD': '',         # Not used with sqlite3.
        'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',             # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = 'Europe/Oslo'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = join(this_dir, "filestore")
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+g$%**q(w78xqa_2)(_+%v8d)he-b_^@d*pqhq!#2p*a7*9e9h'



MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'devilry.apps.core.utils.profile.ProfilerMiddleware'
]


ROOT_URLCONF = 'devilry.urls'

LOGIN_URL = '/ui/login'
DEVILRY_LOGOUT_URL = '/ui/logout'


INSTALLED_APPS = (
    'django.contrib.markup', 
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.webdesign',
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'devilry.apps.core',
    'devilry.apps.ui',
    'devilry.apps.gui',
    'devilry.apps.xmlrpc',

    'devilry.apps.simplified',
    'devilry.apps.restful',

    'devilry.apps.student',
    'devilry.apps.examiner',
    'devilry.apps.xmlrpc_examiner',
    'devilry.apps.admin',
    'devilry.apps.grade_approved',
    'devilry.apps.grade_default',
    'devilry.apps.grade_schema',
    'devilry.apps.grade_rstschema',
    'devilry.apps.quickdash',
    'devilry.apps.gradestats',

    'devilry.apps.xmlrpc_client',
    'devilry.apps.guiexamples',
)




DEVILRY_RESOURCES_ROOT = join(this_dir, 'resources')
DEVILRY_RESOURCES_URL = '/resources'
DEVILRY_THEME_URL = '/resources/gui/themes/devilry'
DEVILRY_EXTJS_URL = '/resources/ext-4.0.1'
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth", 
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.debug",
    'devilry.apps.core.templatecontext.template_variables',
)



DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsDeliveryStore'
DELIVERY_STORE_ROOT = join(this_dir, 'deliverystore')
#DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.DbmDeliveryStore'
#DELIVERY_STORE_DBM_FILENAME = join(this_dir, 'deliverystore', 'deliverystore.dbm')

# Make sure this does not end with / (i.e. '' means / is the main page).
DEVILRY_MAIN_PAGE = ''

# The base template used by devilry. Override for simple theming
BASE_TEMPLATE = 'devilry/base.django.html'

MEDIA_ICONS_URL = 'media/icons/'
JQUERY_UI_THEME = 'devilry-blue'

SEND_EMAIL_TO_USERS = False

## The default grade-plugin
DEVILRY_DEFAULT_GRADEPLUGIN='grade_default:charfieldgrade'
#DEVILRY_DEFAULT_GRADEPLUGIN='grade_default:approvedgrade'
#DEVILRY_DEFAULT_GRADEPLUGIN='grade_rstschema:rstschemagrade'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = this_dir + '/email_log/'

EMAIL_SUBJECT_PREFIX = '[devilry] '
EMAIL_SUBJECT_PREFIX_ADMIN = '[devilry-admin] '

WEB_PAGE_PREFIX = 'http://devilry.ifi.uio.no/django/main'
EMAIL_DEFAULT_FROM = 'devilry-support@ifi.uio.no'
EMAIL_SIGNATURE = "This is a message from the Devilry assignment delivery system. " \
                  "Please do not respond to this email."

DEVILRY_SYSTEM_ADMIN_EMAIL='devilry-support@example.com'

DATETIME_FORMAT = "N j, Y, H:i"

#Set max file size to 5MB. Files greater than this size are split into chunks of this size.
MAX_ARCHIVE_CHUNK_SIZE = 5000000
