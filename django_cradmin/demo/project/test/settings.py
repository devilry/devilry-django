"""
Django settings for running the django_cradmin tests.
"""

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "y%j0x%=7a^sf53m*s^5nbmfe0_t13d*oibfx#m#*wz1x+k6+m1"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_cradmin",
    "django_cradmin.django_cradmin_testapp",
    "django_cradmin.apps.cradmin_generic_token_with_metadata",
    "django_cradmin.apps.cradmin_authenticate",
    "django_cradmin.apps.cradmin_resetpassword",
    "django_cradmin.apps.cradmin_activate_account",
    "django_cradmin.apps.cradmin_register_account",
    "django_cradmin.apps.cradmin_invite",
    "django_cradmin.apps.cradmin_email",
    "django_cradmin.apps.django_cradmin_js",
    "django_cradmin.uicontainer",
    "django_cradmin.tests.test_sortable.cradmin_sortable_testapp",
    "django_cradmin.tests.test_viewhelpers.cradmin_viewhelpers_testapp",
    "django_cradmin.apps.cradmin_authenticate.tests.cradmin_authenticate_testapp",
    "django_cradmin.apps.cradmin_register_account.tests.cradmin_register_account_testapp",
    "django_cradmin.apps.cradmin_email.tests.cradmin_email_testapp",
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
                "django_cradmin.context_processors.cradmin",
            ],
        },
    },
]


# ROOT_URLCONF = 'django_cradmin.demo.project.urls'

# We do not set a name -- the test framework does that.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}

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

ROOT_URLCONF = "django_cradmin.demo.project.test.urls"
DJANGO_CRADMIN_SITENAME = "Testsite"
DJANGO_CRADMIN_REGISTER_ACCOUNT_FORM_CLASS = (
    "django_cradmin.apps.cradmin_register_account.forms.auth_user.AuthUserCreateAccountForm"
)

DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES = True
