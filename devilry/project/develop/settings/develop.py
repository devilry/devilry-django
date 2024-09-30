from ievv_opensource.utils import ievvbuildstatic, ievvdevrun

from .base import *

# MIDDLEWARE = MIDDLEWARE + ['devilry.project.develop.middleware.FakeLoginMiddleware']


# The if's below is just to make it easy to toggle these settings on and off during development
profiler_middleware = False
if profiler_middleware:
    MIDDLEWARE = MIDDLEWARE + [
        "devilry.utils.profile.ProfilerMiddleware",  # Enable profiling. Just add ?prof=yes to any url to see a profile report
    ]

MIDDLEWARE = MIDDLEWARE + [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    #    "whitenoise.middleware.WhiteNoiseMiddleware",
]

# DELAY_MIDDLEWARE_TIME = (80, 120) # Wait for randint(*DELAY_MIDDLEWARE_TIME)/100.0 before responding to each request when using DelayMiddleware
# delay_middleware = True
# if delay_middleware:
#     MIDDLEWARE = MIDDLEWARE + [
#         'devilry.utils.delay_middleware.DelayMiddleware'
#     ]


######################
#
# Django Debug Toolbar
#
######################
INSTALLED_APPS += ["debug_toolbar"]


#######################################################
#
# Django allauth with Dataporten provider
#
#######################################################
INSTALLED_APPS += ["devilry.devilry_dataporten_allauth"]

AUTHENTICATION_BACKENDS += [
    "allauth.account.auth_backends.AuthenticationBackend",
]

DEVILRY_FEIDE_USERID_SEC_TO_USERNAME_SUFFIX = "uio.no"


######################################################
# Email
######################################################

## If you want to test with a "real" smtp server instead of the file backend, see:
##     https://docs.djangoproject.com/en/dev/topics/email/#testing-email-sending
## In short, uncomment the settings below and run the built in smtpd server in python:
##      python -m smtpd -n -c DebuggingServer localhost:1025
## The smtpd server prints emails to stdout.
# EMAIL_BACKEND = 'devilry.devilry_email.rq_backend.RQEmailBackend'
# DEVILRY_LOWLEVEL_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025

# Use the devilry_developemail package to send mails.
# mails are stored in the database and available through /djangoadmin/
# EMAIL_BACKEND = 'devilry.devilry_developemail.email_backend.DevelopEmailBackend'
# INSTALLED_APPS += ['devilry.devilry_developemail']

# For testing RQ email backend
# DEVILRY_LOWLEVEL_EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEVILRY_LOWLEVEL_EMAIL_BACKEND = "ievv_opensource.ievv_developemail.email_backend.DevelopEmailBackend"
EMAIL_BACKEND = "devilry.devilry_email.rq_backend.RQEmailBackend"


# DEVILRY_FRONTPAGE_HEADER_INCLUDE_TEMPLATE = 'devilry_theme3/include/includetest.django.html'
# DEVILRY_FRONTPAGE_FOOTER_INCLUDE_TEMPLATE = 'devilry_theme3/include/includetest.django.html'
# DEVILRY_HELP_PAGE_HEADER_INCLUDE_TEMPLATE = 'devilry_theme3/include/includetest.django.html'
# DEVILRY_HELP_PAGE_FOOTER_INCLUDE_TEMPLATE = 'devilry_theme3/include/includetest.django.html'
# DEVILRY_PROFILEPAGE_HEADER_INCLUDE_TEMPLATE = 'devilry_theme3/include/includetest.django.html'
# DEVILRY_PROFILEPAGE_FOOTER_INCLUDE_TEMPLATE = 'devilry_theme3/include/includetest.django.html'

# Disable migrations when running tests
# class DisableMigrations(object):
#
#     def __contains__(self, item):
#         return True
#
#     def __getitem__(self, item):
#         return "notmigrations"
#
# MIGRATION_MODULES = DisableMigrations()


LANGUAGE_CODE = "nb"

IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
    ievvbuildstatic.config.App(
        appname="devilry_theme3",
        version=devilry.__version__,
        plugins=[
            ievvbuildstatic.bowerinstall.Plugin(
                packages={
                    "bootstrap": "~3.1.1",
                    "fontawesome": "~4.3.0",
                }
            ),
            ievvbuildstatic.lessbuild.Plugin(
                sourcefolder="styles/cradmin_theme_devilry_mainpages",
                sourcefile="theme.less",
                other_sourcefolders=[
                    "styles/cradmin_base",
                    "styles/cradmin_theme_topmenu",
                    "styles/cradmin_theme_devilry_common",
                ],
                less_include_paths=[
                    "bower_components",
                ],
            ),
            ievvbuildstatic.lessbuild.Plugin(
                sourcefolder="styles/cradmin_theme_devilry_superuserui",
                sourcefile="theme.less",
                other_sourcefolders=[
                    "styles/cradmin_base",
                    "styles/cradmin_theme_default",
                    "styles/cradmin_theme_devilry_common",
                ],
                less_include_paths=[
                    "bower_components",
                ],
            ),
            ievvbuildstatic.npmrun_jsbuild.Plugin(),
            ievvbuildstatic.mediacopy.Plugin(),
            ievvbuildstatic.mediacopy.Plugin(sourcefolder="scripts/plain_es6"),
            ievvbuildstatic.nodemodulescopy.Plugin(
                destinationfolder=os.path.join("scripts", "katex"),
                sourcefiles=[
                    "katex/LICENSE",
                    "katex/dist/katex.mjs",
                    "katex/dist/katex.min.css",
                ],
            ),
            ievvbuildstatic.mediacopy.Plugin(
                sourcefolder="node_modules/katex/dist/fonts",
                destinationfolder=os.path.join("scripts", "katex", "fonts"),
            ),
            ievvbuildstatic.mediacopy.Plugin(
                sourcefolder="node_modules/katex/dist/contrib",
                destinationfolder=os.path.join("scripts", "katex", "contrib"),
            ),
            ievvbuildstatic.mediacopy.Plugin(
                sourcefolder="bower_components/bootstrap/fonts",
                destinationfolder=os.path.join("vendor", "fonts", "glyphicons"),
            ),
        ],
    ),
    ievvbuildstatic.config.App(
        appname="devilry_statistics",
        version=devilry.__version__,
        plugins=[
            ievvbuildstatic.npmrun_jsbuild.Plugin(),
            # ievvbuildstatic.mediacopy.Plugin(),
        ],
    ),
)


IEVVTASKS_DEVRUN_RUNNABLES = {
    "default": ievvdevrun.config.RunnableThreadList(
        ievvdevrun.runnables.django_runserver.RunnableThread(port=8000),
        ievvdevrun.runnables.rq_worker.RunnableThread(),
        ievvdevrun.runnables.rq_worker.RunnableThread(queuename="email"),
    ),
    # Same as default, but Django serves staticfiles if DEBUG=False.
    # Should only be used if anything needs to be tested with DEBUG=False.
    "insecure": ievvdevrun.config.RunnableThreadList(
        ievvdevrun.runnables.django_runserver.RunnableThread(port=8000, insecure=True),
        ievvdevrun.runnables.rq_worker.RunnableThread(),
        ievvdevrun.runnables.rq_worker.RunnableThread(queuename="email"),
    ),
    "gunicorn_test": ievvdevrun.config.RunnableThreadList(
        ievvdevrun.runnables.rq_worker.RunnableThread(),
        ievvdevrun.runnables.rq_worker.RunnableThread(queuename="email"),
    ),
    "design": ievvdevrun.config.RunnableThreadList(
        ievvdevrun.runnables.django_runserver.RunnableThread(),
        ievvdevrun.runnables.ievv_buildstatic.RunnableThread(),
        ievvdevrun.runnables.rq_worker.RunnableThread(),
        ievvdevrun.runnables.rq_worker.RunnableThread(queuename="email"),
    ),
}

IEVVTASKS_DOCS_DASH_NAME = "Devilry"

IEVVTASKS_RECREATE_DEVDB_POST_MANAGEMENT_COMMANDS = [
    {
        "name": "ievvtasks_customsql",
        "args": ["-i", "-r"],
    },
]

IEVVTASKS_MAKEMESSAGES_LANGUAGE_CODES = [
    "en",
    "nb",
]
IEVVTASKS_MAKEMESSAGES_BUILD_JAVASCRIPT_TRANSLATIONS = True
IEVVTASKS_MAKEMESSAGES_JAVASCRIPT_IGNORE = [
    "node_modules/*",
    "not_for_deploy/*",
    "static/*",
    "source/*",
]
IEVVTASKS_MAKEMESSAGES_JAVASCRIPT_EXTENSIONS = [".js"]

IEVVTASKS_MAKEMESSAGES_DIRECTORIES = [
    {"directory": "devilry", "python": True, "javascript": True},
]


# ievv_batchframework task mode.
# IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS = True

# CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND = False


# DEVILRY_V2_DATABASE_SHOULD_CLEAN = True
# DEVILRY_V2_MEDIA_ROOT = None
# DEVILRY_V2_DELIVERY_FILE_ROOT = None
# DEVILRY_RESTRICT_NUMBER_OF_FILES_PER_DIRECTORY = True


# For testing custom deploy templates (see branding.rst)
# from devilry.utils.custom_templates import add_custom_templates_directory
# add_custom_templates_directory(
#     TEMPLATES, 'not_for_deploy/custom_devilry_templates_example/')

###################################################################################
# RQ
###################################################################################

# Uncomment these line to run RQ synchronously.
# RQ_QUEUES['default']['ASYNC'] = False
# RQ_QUEUES['email']['ASYNC'] = False
# RQ_QUEUES['highpriority']['ASYNC'] = False


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda r: False,  # comment this out to enable debug toolbar
}


DEVILRY_ASSIGNMENT_GUIDELINES = {
    "student": [
        (
            r"duck10.+",
            {
                "__version__": "1",
                "__default__": {
                    "htmltext": "This is the assignment guidelines for duck10xx courses.",
                    "url": "http://example.com",
                },
                "nb": {
                    "htmltext": "Dette er retningslinjene for oppgaver i duck10xx kurs",
                    "url": "http://vg.no",
                },
            },
        ),
        (
            r"duck11.+",
            {
                "__version__": "1",
                "__default__": {
                    "htmltext": "This is the assignment guidelines for duck11xx courses.",
                    "url": "http://example.com",
                },
                "nb": {
                    "htmltext": "Dette er retningslinjene for oppgaver i duck11xx kurs",
                    "url": "http://vg.no",
                },
            },
        ),
    ]
}

DELIVERY_STORAGE_BACKEND = "devilry_delivery_storage"
DELIVERY_STORAGE_BACKEND_GENERATE_URLS = "devilry_delivery_storage_generate_urls"
DELIVERY_TEMPORARY_STORAGE_BACKEND = "devilry_temp_storage"
DELIVERY_TEMPORARY_STORAGE_BACKEND_GENERATE_URLS = "devilry_temp_storage_generate_urls"
CRADMIN_LEGACY_TEMPORARY_FILE_STORAGE_BACKEND = "devilry_temp_storage"

# Without this setting, django-storages uses a lot of memory. With this setting,
# files over this size (in bytes) will be written to a temporary file on disk
# during transfer to/from S3
AWS_S3_MAX_MEMORY_SIZE = 1024 * 1024 * 8  # 8MB

# Tune transfer config for stable memory usage and for gevent
from boto3.s3.transfer import TransferConfig

AWS_S3_TRANSFER_CONFIG = TransferConfig(
    use_threads=False,  # MUST be False when using gevent worker
    io_chunksize=1024 * 1024 * 8,  # 8MB
    max_io_queue=4,
    multipart_chunksize=1024 * 1024 * 8,  # 8MB
    multipart_threshold=1024 * 1024 * 8,  # 8MB
)

# This defaults to True, and it MUST be True for devilry to work correctly
AWS_S3_FILE_OVERWRITE = True

STORAGES = {
    "devilry_delivery_storage": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            # region_name: ''  # Needed for AWS, but not for all S3 compatible storages
            "endpoint_url": "http://localhost:9000",
            "bucket_name": "devilrydeliverystorage",
            "access_key": "testuser",
            "secret_key": "testpassword",
        },
    },
    "devilry_delivery_storage_generate_urls": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            # region_name: ''  # Needed for AWS, but not for all S3 compatible storages
            "endpoint_url": "http://localhost:9000",
            "bucket_name": "devilrydeliverystorage",
            "access_key": "testuser",
            "secret_key": "testpassword",
        },
    },
    "devilry_temp_storage": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            # region_name: ''  # Needed for AWS, but not for all S3 compatible storages
            "endpoint_url": "http://localhost:9000",
            "bucket_name": "devilrytempstorage",
            "access_key": "testuser",
            "secret_key": "testpassword",
        },
    },
    "devilry_temp_storage_generate_urls": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            # region_name: ''  # Needed for AWS, but not for all S3 compatible storages
            "endpoint_url": "http://localhost:9000",
            "bucket_name": "devilrytempstorage",
            "access_key": "testuser",
            "secret_key": "testpassword",
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        "OPTIONS": {"location": "staticfiles"},
    },
}

DEVILRY_USE_STORAGE_BACKEND_URL_FOR_ARCHIVE_DOWNLOADS = True
DEVILRY_USE_STORAGE_BACKEND_URL_FOR_FILE_DOWNLOADS = True


DEVILRY_MEMORY_DEBUG_ENABLED = True
