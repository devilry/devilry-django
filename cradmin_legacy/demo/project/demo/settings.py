"""
Django settings for cradmin demo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

THIS_DIR = os.path.dirname(__file__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "y%j0x%=7a^sf53m*s^5nbmfe0_t13d*oibfx#m#*wz1x+k6+m1"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.forms",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Required by django cradmin
    "cradmin_legacy",
    "cradmin_legacy.apps.cradmin_imagearchive.apps.ImageArchiveConfig",
    "cradmin_legacy.apps.cradmin_temporaryfileuploadstore",
    "django_cradmin.apps.cradmin_generic_token_with_metadata",
    "cradmin_legacy.apps.cradmin_authenticate",
    "cradmin_legacy.apps.cradmin_resetpassword",
    "cradmin_legacy.apps.cradmin_activate_account",
    "cradmin_legacy.apps.cradmin_register_account",
    "cradmin_legacy.apps.cradmin_invite",
    "cradmin_legacy.apps.cradmin_email",
    "crispy_forms",
    "sorl.thumbnail",  # Required by cradmin_imagearchive
    # Just here to get the demo overview view.
    "cradmin_legacy.demo.project.demo",
    # The advanced demo
    "cradmin_legacy.demo.webdemo.apps.WebdemoConfig",
    "cradmin_legacy.demo.login_not_required_demo",
    "cradmin_legacy.demo.no_role_demo",
    # The demo based on the Django tutorial
    "cradmin_legacy.demo.polls_demo",
    # Demo for usermanager
    "cradmin_legacy.demo.usermanagerdemo.apps.UsermanagerdemoConfig",
    # Demo for listfilter
    "cradmin_legacy.demo.listfilterdemo",
    # Demo for multiselect
    "cradmin_legacy.demo.multiselect2demo.apps.MultiselectdemoConfig",
    # For building docs
    "ievv_opensource.ievvtasks_development",
)

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 'cradmin_legacy.delay_middleware.DelayMiddleware',
)
# CRADMIN_LEGACY_DELAY_MIDDLEWARE_MILLISECONDS = 2000

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
                "cradmin_legacy.context_processors.cradmin",
            ],
        },
    },
]

ROOT_URLCONF = "cradmin_legacy.demo.project.demo.urls"

# WSGI_APPLICATION = 'cradmin_legacy.demo.wsgi.application'

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "devdb.sqlite3"}}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = "/static/"

# Django crispy forms:
CRISPY_TEMPLATE_PACK = "bootstrap3"

# Thumbnails (sorl-thumbnail)
# See: http://sorl-thumbnail.readthedocs.org/en/latest/reference/settings.html
THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pil_engine.Engine"
THUMBNAIL_KVSTORE = "sorl.thumbnail.kvstores.cached_db_kvstore.KVStore"
THUMBNAIL_PREFIX = "sorlcache/"
THUMBNAIL_DEBUG = False

# The root for file fileuploads
MEDIA_ROOT = os.path.join(BASE_DIR, "django_media_root")
STATIC_ROOT = os.path.join(BASE_DIR, "django_static_root")

MEDIA_URL = "/media/"

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

CRADMIN_LEGACY_SITENAME = "Cradmin demo"
CRADMIN_LEGACY_RESETPASSWORD_FINISHED_REDIRECT_URL = LOGIN_REDIRECT_URL
CRADMIN_LEGACY_FORGOTPASSWORD_URL = "/resetpassword/begin"

CRADMIN_LEGACY_REGISTER_ACCOUNT_FORM_CLASS = (
    "cradmin_legacy.apps.cradmin_register_account.forms.auth_user.AuthUserCreateAccountAutoUsernameForm"
)
# CRADMIN_LEGACY_REGISTER_ACCOUNT_FORM_CLASS = \
#     'cradmin_legacy.apps.cradmin_register_account.forms.auth_user.AuthUserCreateAccountForm'


CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND = True

AUTHENTICATION_BACKENDS = ("cradmin_legacy.apps.cradmin_authenticate.backends.EmailAuthBackend",)
TIME_INPUT_FORMATS = [
    "%H:%M",  # '14:30'
    "%H:%M:%S",  # '14:30:59'
]

# CRADMIN_LEGACY_THEME_PATH = 'cradmin_legacy/dist/css/cradmin_theme_topmenu/theme.css'
CRADMIN_LEGACY_MENU_SCROLL_TOP_FIXED = True
# CRADMIN_LEGACY_MOMENTJS_LOCALE = 'nb'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = "en-us"
# LANGUAGE_CODE = 'nb'

TIME_ZONE = "Europe/Oslo"

USE_I18N = True

USE_L10N = True

USE_TZ = True


CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP = {
    "cradmin-webdemo-pages-listing": {
        "width": 300,
        "height": 200,
        "crop": "lfill",
        "quality": 70,
    },
    "cradmin-archiveimage-listing": {
        "width": 170,
        "height": 100,
        "crop": "lfill",
        "quality": 70,
    },
    "cradmin-archiveimage-preview": {
        "width": 330,
        "height": 400,
        "crop": "limit",
        "quality": 70,
    },
}

CRADMIN_LEGACY_IMAGEARCHIVE_LISTING_IMAGETYPE = "cradmin-archiveimage-listing"
CRADMIN_LEGACY_IMAGEARCHIVE_LISTING_IMAGEWIDTH = 170
CRADMIN_LEGACY_IMAGEARCHIVE_PREVIEW_IMAGETYPE = "cradmin-archiveimage-preview"
# CRADMIN_LEGACY_IMAGEARCHIVE_MAX_FILESIZE = '100KB'


IEVVTASKS_DOCS_DIRECTORY = "docs"
IEVVTASKS_DOCS_DASH_NAME = "cradmin"
