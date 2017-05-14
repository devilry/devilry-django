from ievv_opensource.utils import ievvdevrun
from ievv_opensource.utils import ievvbuildstatic
from .base import *

# MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ['devilry.project.develop.middleware.FakeLoginMiddleware']

#: Where to store compressed archives for filedownloads
DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY = os.path.join(developfilesdir, 'devilry_compressed_archives', '')

# The if's below is just to make it easy to toggle these settings on and off during development
profiler_middleware = False
if profiler_middleware:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + [
        'devilry.utils.profile.ProfilerMiddleware', # Enable profiling. Just add ?prof=yes to any url to see a profile report
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

# DELAY_MIDDLEWARE_TIME = (80, 120) # Wait for randint(*DELAY_MIDDLEWARE_TIME)/100.0 before responding to each request when using DelayMiddleware
# delay_middleware = True
# if delay_middleware:
#     MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + [
#         'devilry.utils.delay_middleware.DelayMiddleware'
#     ]


INSTALLED_APPS += [
    # 'debug_toolbar',
]


##################################################################################
# Celery
##################################################################################
CELERY_ALWAYS_EAGER = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_EAGER_TRANSACTION = True

## For testing celery
## - Se the "Developing and testing Celery background tasks" chapter of the developer docs.
# CELERY_ALWAYS_EAGER = False
# BROKER_URL = 'amqp://'
# CELERY_RESULT_BACKEND = 'amqp://'


######################################################
# Email
######################################################

## If you want to test with a "real" smtp server instead of the file backend, see:
##     https://docs.djangoproject.com/en/dev/topics/email/#testing-email-sending
## In short, uncomment the settings below and run the built in smtpd server in python:
##      python -m smtpd -n -c DebuggingServer localhost:1025
## The smtpd server prints emails to stdout.
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'localhost'
#EMAIL_PORT = 1025

# Use the devilry_developemail package to send mails.
# mails are stored in the database and available through /djangoadmin/
# EMAIL_BACKEND = 'devilry.devilry_developemail.email_backend.DevelopEmailBackend'
# INSTALLED_APPS += ['devilry.devilry_developemail']


# For testing django-celery-email
# INSTALLED_APPS += ['djcelery_email']
# EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
# CELERY_EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

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


# LANGUAGE_CODE = 'nb'


IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
    ievvbuildstatic.config.App(
        appname='devilry_theme3',
        version=DEVILRY_THEME3_VERSION,
        plugins=[
            ievvbuildstatic.bowerinstall.Plugin(
                packages={
                    'bootstrap': '~3.1.1',
                    'fontawesome': '~4.3.0',
                }
            ),
            ievvbuildstatic.lessbuild.Plugin(
                sourcefolder='styles/cradmin_theme_devilry_mainpages',
                sourcefile='theme.less',
                other_sourcefolders=[
                    'styles/cradmin_base',
                    'styles/cradmin_theme_topmenu',
                    'styles/cradmin_theme_devilry_common',
                ],
                less_include_paths=[
                    'bower_components',
                ]
            ),
            ievvbuildstatic.lessbuild.Plugin(
                sourcefolder='styles/cradmin_theme_devilry_superuserui',
                sourcefile='theme.less',
                other_sourcefolders=[
                    'styles/cradmin_base',
                    'styles/cradmin_theme_default',
                    'styles/cradmin_theme_devilry_common',
                ],
                less_include_paths=[
                    'bower_components',
                ]
            ),
            ievvbuildstatic.npmrun_jsbuild.Plugin(),
            ievvbuildstatic.mediacopy.Plugin(),
        ]
    ),
)


IEVVTASKS_DEVRUN_RUNNABLES = {
    'default': ievvdevrun.config.RunnableThreadList(
        ievvdevrun.runnables.dbdev_runserver.RunnableThread(),
        ievvdevrun.runnables.django_runserver.RunnableThread(),
        ievvdevrun.runnables.redis_server.RunnableThread(),
        ievvdevrun.runnables.celery_worker.RunnableThread(app='devilry.project.common'),
    ),
    'design': ievvdevrun.config.RunnableThreadList(
        ievvdevrun.runnables.dbdev_runserver.RunnableThread(),
        ievvdevrun.runnables.django_runserver.RunnableThread(),
        ievvdevrun.runnables.ievv_buildstatic.RunnableThread(),
        ievvdevrun.runnables.redis_server.RunnableThread(),
        ievvdevrun.runnables.celery_worker.RunnableThread(app='devilry.project.common'),
    ),
}

IEVVTASKS_DOCS_DASH_NAME = 'Devilry'

IEVVTASKS_RECREATE_DEVDB_POST_MANAGEMENT_COMMANDS = [
    {
        'name': 'ievvtasks_customsql',
        'args': ['-i', '-r'],
    },
]
