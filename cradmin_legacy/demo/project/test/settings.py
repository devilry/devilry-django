"""
Django settings for running the cradmin_legacy tests.
"""

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "y%j0x%=7a^sf53m*s^5nbmfe0_t13d*oibfx#m#*wz1x+k6+m1"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.forms",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cradmin_legacy",
    "cradmin_legacy.cradmin_legacy_testapp",
    "cradmin_legacy.apps.cradmin_imagearchive",
    "cradmin_legacy.apps.cradmin_temporaryfileuploadstore",
    "django_cradmin.apps.cradmin_generic_token_with_metadata",
    "cradmin_legacy.apps.cradmin_authenticate",
    "cradmin_legacy.apps.cradmin_resetpassword",
    "cradmin_legacy.apps.cradmin_activate_account",
    "cradmin_legacy.apps.cradmin_register_account",
    "cradmin_legacy.apps.cradmin_invite",
    "cradmin_legacy.apps.cradmin_email",
    "cradmin_legacy.tests.sortable.cradmin_sortable_testapp",
    "cradmin_legacy.tests.viewhelpers.cradmin_viewhelpers_testapp",
    "cradmin_legacy.tests.test_automodelform.cradmin_automodelform_testapp",
    "cradmin_legacy.apps.cradmin_authenticate.tests.cradmin_authenticate_testapp",
    "cradmin_legacy.apps.cradmin_register_account.tests.cradmin_register_account_testapp",
    "cradmin_legacy.apps.cradmin_email.tests.cradmin_email_testapp",
    # Required by django cradmin
    "crispy_forms",
    "sorl.thumbnail",  # Required by cradmin_imagearchive
    # Demo apps
    "cradmin_legacy.demo.webdemo",
    "cradmin_legacy.demo.polls_demo",
    "cradmin_legacy.demo.usermanagerdemo",
    "cradmin_legacy.demo.listfilterdemo",
    "cradmin_legacy.demo.multiselect2demo",
)

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

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


# ROOT_URLCONF = 'cradmin_legacy.demo.project.urls'

# We do not set a name -- the test framework does that.
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "devdb.sqlite3"}}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = "/static/"

MEDIA_ROOT = "test_django_media_root"
STATIC_ROOT = "test_django_static_root"

# Django crispy forms:
CRISPY_TEMPLATE_PACK = "bootstrap3"

ROOT_URLCONF = "cradmin_legacy.demo.project.test.urls"
CRADMIN_LEGACY_SITENAME = "Testsite"
CRADMIN_LEGACY_REGISTER_ACCOUNT_FORM_CLASS = (
    "cradmin_legacy.apps.cradmin_register_account.forms.auth_user.AuthUserCreateAccountForm"
)
