# Django settings for devilry project.
from os.path import abspath, dirname, join

this_dir = dirname(abspath(__file__))


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = join(this_dir, 'db.sqlite3') # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Oslo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = join(this_dir, "filestore")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+g$%**q(w78xqa_2)(_+%v8d)he-b_^@d*pqhq!#2p*a7*9e9h'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
]


ROOT_URLCONF = 'devilry.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(this_dir, 'templates')
)


LOGIN_URL = '/ui/login'
DEVILRY_LOGOUT_URL = '/ui/logout'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
	'django.contrib.admin',
    #'django.contrib.admindocs',
    'devilry.core',
    'devilry.ui',
    'devilry.addons.student',
    'devilry.addons.examiner',
    'devilry.addons.admin',
    'devilry.addons.grade_approved',
    'devilry.addons.grade_default',
    'devilry.addons.grade_schema',
    'devilry.addons.grade_rstschema',
    'devilry.addons.dashboard',
    'devilry.xmlrpc',
    'devilry.addons.xmlrpc_examiner',
    'devilry.xmlrpc_client',
    'django.contrib.markup', 
    )


DEVILRY_RESOURCES_ROOT = join(this_dir, 'resources')
DEVILRY_RESOURCES_URL = '/resources'
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth", 
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'devilry.core.templatecontext.template_variables',
)



#DELIVERY_STORE_BACKEND = 'devilry.core.deliverystore.FsDeliveryStore'
#DELIVERY_STORE_ROOT = join(this_dir, 'deliverystore')
DELIVERY_STORE_BACKEND = 'devilry.core.deliverystore.DbmDeliveryStore'
DELIVERY_STORE_DBM_FILENAME = join(this_dir, 'deliverystore.dbm')

# Make sure this does not end with / (i.e. '' means / is the main page).
DEVILRY_MAIN_PAGE = ''

# The base template used by devilry. Override for simple theming
BASE_TEMPLATE = 'devilry/base.django.html'

MEDIA_ICONS_URL = 'media/icons/'
JQUERY_UI_THEME = 'blitzer'


## The default grade-plugin
DEVILRY_DEFAULT_GRADEPLUGIN='grade_default:charfieldgrade'
#DEVILRY_DEFAULT_GRADEPLUGIN='grade_default:approvedgrade'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = this_dir + '/email_log/'

#EMAIL_HOST = 'smtp.ifi.uio.no'
#EMAIL_PORT = 25

#EMAIL_HOST_USER = 
#EMAIL_HOST_PASSWORD = 

email_subject_prefix = '[devilry] '
