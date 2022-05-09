from .base import *  # noqa


# We want to set the task to be run as syncronous as this make testing easier.
IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS = True

testfilesdir = 'devilry_testfiles'
if not exists(testfilesdir):
    os.mkdir(testfilesdir)
logdir = join(testfilesdir, 'log')
if not exists(logdir):
    os.mkdir(logdir)
MEDIA_ROOT = join(testfilesdir, "filestore")
DEVILRY_FSHIERDELIVERYSTORE_ROOT = join(testfilesdir, 'deliverystorehier')

#: Where to store compressed archives for download.
DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY = os.path.join(testfilesdir, 'devilry_compressed_archives', '')

#: Remove tracback logging middleware when running tests.
if 'devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('devilry.utils.logexceptionsmiddleware.TracebackLoggingMiddleware')

#: Remove django toolbar middleware while running tests.
if 'debug_toolbar.middleware.DebugToolbarMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

#: Remove django toolbar from installed apps.
INSTALLED_APPS += [
    'devilry.devilry_dbcache.devilry_dbcache_testapp',
]

if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

# We need to use this because loads of tests uses username and password to login
CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND = False
AUTHENTICATION_BACKENDS = (
    'devilry.devilry_account.authbackend.default.UsernameAuthBackend',
    'devilry.devilry_account.authbackend.default.EmailAuthBackend',
)

# Ensures we are testing against the default translation strings.
DEVILRY_JAVASCRIPT_LOCALE_OVERRIDE_APPS = []

# Default to skipping selenium tests
SKIP_SELENIUMTESTS = True
# SELENIUM_BROWSER = 'phantomjs'
# SELENIUM_DEFAULT_TIMEOUT = 20


# Disable migrations when running tests
class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

    # def __getitem__(self, key):
    #     return 'notmigrations'


# Add this to run a database for anonymization
# DATABASES['anonymize_db'] = DATABASES['default'].copy()
# DATABASES['anonymize_db']['NAME'] = 'dbdev_anonymize'


MIGRATION_MODULES = DisableMigrations()

# DEVILRY_V2_DATABASE_MAX_BULK_CREATE_OVERRIDE = 100
DEVILRY_V2_DATABASE_PRINT_PROGRESS_DOTS = False

# Enable test css-classes
DEVILRY_INCLUDE_TEST_CSS_CLASSES = True

###################################################################################
# RQ
###################################################################################

# RQ runs synchronously by default for tests.
RQ_QUEUES['default']['ASYNC'] = False
RQ_QUEUES['email']['ASYNC'] = False
RQ_QUEUES['highpriority']['ASYNC'] = False
