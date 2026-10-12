"""
Django settings for cradmin demo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os

from ievv_opensource.utils import ievvbuildstatic, ievvdevrun

import django_cradmin

THIS_DIR = os.path.dirname(__file__)
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "y%j0x%=7a^sf53m*s^5nbmfe0_t13d*oibfx#m#*wz1x+k6+m1"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "cradmin.dev",
    "cradmin.test",
]


# Application definition

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    # Required by django cradmin
    "django_cradmin",
    "django_cradmin.apps.cradmin_generic_token_with_metadata",
    "django_cradmin.apps.cradmin_authenticate",
    "django_cradmin.apps.cradmin_resetpassword",
    "django_cradmin.apps.cradmin_activate_account",
    "django_cradmin.apps.cradmin_register_account",
    "django_cradmin.apps.cradmin_invite",
    "django_cradmin.apps.cradmin_email",
    "django_cradmin.apps.django_cradmin_js",
    "django_cradmin.apps.django_cradmin_styles",
    "django_cradmin.deprecated_apps.cradmin_imagearchive",
    "django_cradmin.deprecated_apps.cradmin_temporaryfileuploadstore",
    "django_cradmin.uicontainer",
    # Just here to get the demo overview view.
    "django_cradmin.demo.project.demo",
    "django_cradmin.demo.no_role_demo",
    #: Demo for django_cradmin.uicontainer
    "django_cradmin.demo.uicontainerdemo",
    #: Demo for creating a custom cradmin theme
    # 'django_cradmin.demo.custom_theme_demo',
    #: Demo for the javascript components
    "django_cradmin.demo.cradmin_javascript_demos",
    #: Demo for viewhelpers.uimock
    "django_cradmin.demo.uimock_demo",
    "ievv_opensource.ievvtasks_development",
    "ievv_opensource.ievvtasks_common",
)

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 'django_cradmin.delay_middleware.DelayMiddleware',
    # 'django_cradmin.messages_debug_middleware.MessagesDebugMiddleware',
)
# DJANGO_CRADMIN_DELAY_MIDDLEWARE_MILLISECONDS = 2000

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # insert your TEMPLATE_DIRS here
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": True,
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "django_cradmin.context_processors.cradmin",
            ],
        },
    },
]

ROOT_URLCONF = "django_cradmin.demo.project.demo.urls"

# WSGI_APPLICATION = 'django_cradmin.demo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "dbdev.sqlite3",
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = "/static/"


# The root for file fileuploads
MEDIA_ROOT = os.path.join(BASE_DIR, "django_media_root")
STATIC_ROOT = os.path.join(BASE_DIR, "django_static_root")

MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"verbose": {"format": "[%(levelname)s %(asctime)s %(name)s %(pathname)s:%(lineno)s] %(message)s"}},
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {"stderr": {"level": "DEBUG", "formatter": "verbose", "class": "logging.StreamHandler"}},
    "loggers": {
        "django.request": {"handlers": ["stderr"], "level": "DEBUG", "propagate": False},
        "django.db": {
            "handlers": ["stderr"],
            "level": "INFO",  # Do not set to debug - logs all queries
            "propagate": False,
        },
        "sh": {"handlers": ["stderr"], "level": "WARNING", "propagate": False},
        "": {"handlers": ["stderr"], "level": "DEBUG", "propagate": False},
    },
}

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/authenticate/login"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DJANGO_CRADMIN_SITENAME = "Cradmin demo"
DJANGO_CRADMIN_RESETPASSWORD_FINISHED_REDIRECT_URL = LOGIN_REDIRECT_URL
DJANGO_CRADMIN_FORGOTPASSWORD_URL = "/resetpassword/begin"

DJANGO_CRADMIN_REGISTER_ACCOUNT_FORM_CLASS = (
    "django_cradmin.apps.cradmin_register_account.forms.auth_user.AuthUserCreateAccountAutoUsernameForm"
)
# DJANGO_CRADMIN_REGISTER_ACCOUNT_FORM_CLASS = \
#     'django_cradmin.apps.cradmin_register_account.forms.auth_user.AuthUserCreateAccountForm'


DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND = True

AUTHENTICATION_BACKENDS = ("django_cradmin.apps.cradmin_authenticate.backends.EmailAuthBackend",)
TIME_INPUT_FORMATS = [
    "%H:%M",  # '14:30'
    "%H:%M:%S",  # '14:30:59'
]

# DJANGO_CRADMIN_THEME_PATH = 'django_cradmin/dist/css/cradmin_theme_topmenu/theme.css'
DJANGO_CRADMIN_MENU_SCROLL_TOP_FIXED = True
# DJANGO_CRADMIN_MOMENTJS_LOCALE = 'nb'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = "en-us"
# LANGUAGE_CODE = 'nb'

TIME_ZONE = "Europe/Oslo"

USE_I18N = True

USE_L10N = True

USE_TZ = True


IEVVTASKS_DOCS_DIRECTORY = "docs"
IEVVTASKS_DOCS_DASH_NAME = "cradmin"


IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
    ievvbuildstatic.config.App(
        appname="django_cradmin_styles",
        version=django_cradmin.__version__,
        # keep_temporary_files=True,
        plugins=[
            ievvbuildstatic.mediacopy.Plugin(),
            ievvbuildstatic.sassbuild.Plugin(sourcefolder="styles/basetheme", sourcefile="main.scss"),
            ievvbuildstatic.sassbuild.Plugin(sourcefolder="styles/basetheme", sourcefile="styleguide.scss"),
        ],
    ),
    ievvbuildstatic.config.App(
        appname="django_cradmin_js",
        version=django_cradmin.__version__,
        # keep_temporary_files=True,
        plugins=[
            ievvbuildstatic.npmrun_jsbuild.Plugin(),
        ],
    ),
    # ievvbuildstatic.config.App(
    #     appname='custom_theme_demo',
    #     version='2.0.1',
    #     plugins=[
    #         ievvbuildstatic.mediacopy.Plugin(
    #             sourcefolder=ievvbuildstatic.filepath.SourcePath('django_cradmin', 'media'),
    #             destinationfolder='media'
    #         ),
    #         ievvbuildstatic.sassbuild.Plugin(
    #             sourcefolder='styles/cradmin_theme_example',
    #             sourcefile='main.scss',
    #             minify=False,
    #             other_sourcefolders=[
    #                 ievvbuildstatic.filepath.SourcePath('django_cradmin', 'styles', 'cradmin_theme_default'),
    #             ],
    #             sass_include_paths=[
    #                 ievvbuildstatic.filepath.SourcePath('django_cradmin', 'styles')
    #             ]
    #         ),
    #         ievvbuildstatic.sassbuild.Plugin(
    #             sourcefolder='styles/cradmin_theme_example',
    #             sourcefile='styleguide.scss',
    #             minify=False,
    #             other_sourcefolders=[
    #                 ievvbuildstatic.filepath.SourcePath('django_cradmin', 'styles', 'cradmin_theme_default'),
    #             ],
    #             sass_include_paths=[
    #                 ievvbuildstatic.filepath.SourcePath('django_cradmin', 'styles')
    #             ]
    #         ),
    #     ]
    #
    # )
)

IEVVTASKS_DEVRUN_RUNNABLES = {
    "default": ievvdevrun.config.RunnableThreadList(
        ievvdevrun.runnables.django_runserver.RunnableThread(),
    ),
    "default-port-9001": ievvdevrun.config.RunnableThreadList(
        ievvdevrun.runnables.django_runserver.RunnableThread(port=9001),
    ),
    "design": ievvdevrun.config.RunnableThreadList(
        ievvdevrun.runnables.django_runserver.RunnableThread(),
        ievvdevrun.runnables.ievv_buildstatic.RunnableThread(),
    ),
    "design-port-9001": ievvdevrun.config.RunnableThreadList(
        ievvdevrun.runnables.django_runserver.RunnableThread(port=9001),
        ievvdevrun.runnables.ievv_buildstatic.RunnableThread(),
    ),
}


DJANGO_CRADMIN_THEME_PATH = "django_cradmin_styles/{version}/styles/basetheme/main.css".format(
    version=django_cradmin.__version__
)


IEVVTASKS_DUMPDATA_DIRECTORY = os.path.join(THIS_DIR, "dumps")

IEVVTASKS_MAKEMESSAGES_LANGUAGE_CODES = ["en", "nb"]
IEVVTASKS_MAKEMESSAGES_JAVASCRIPT_IGNORE = [
    "node_modules/*",
    "bower_components/*",
    "docs/*",
    "demo/*",
    "static/*",
]
IEVVTASKS_MAKEMESSAGES_DIRECTORIES = [os.path.dirname(django_cradmin.__file__)]

# IEVV_STATICFILES_AUTOGZIP = {
#     'cradmin-theme-css': True
# }
