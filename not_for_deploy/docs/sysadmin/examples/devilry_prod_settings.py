# Import the default settings from devilry
from devilry_settings.default_settings import *


#################################################################################
# Configure the database
#################################################################################
DATABASES = {}
DATABASES["default"] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'djangodb',
    'USER': 'djangouser',
    'PASSWORD': 'supersecret',
    'HOST': 'localhost',
}


##################################################################################
# Make Devilry speak in typical university terms (semester instead of period, ...)
##################################################################################
INSTALLED_APPS += ['devilry_university_translations']
DEVILRY_JAVASCRIPT_LOCALE_OVERRIDE_APPS = ('devilry_university_translations',)


#################################################################################
# Email settings
#################################################################################

#: Default from email - students receive emails from this address when they make deliveries
DEVILRY_EMAIL_DEFAULT_FROM = 'devilry-support@example.com'

#: The URL that is used to link back to devilry from emails
DEVILRY_SCHEME_AND_DOMAIN = 'https://devilry.example.com'

#: Configure an email backend (see the docs for more info)
#EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
#CELERY_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''
#EMAIL_PORT = 25
#EMAIL_USE_TLS = False

##################################################################################
# Other settings
##################################################################################

#: Where should Devilry store your files
DEVILRY_FSHIERDELIVERYSTORE_ROOT = '/devilry-filestorage'

#: Randomize this, and keep it secret
SECRET_KEY = '+g$%**q(w78xqa_2)(_+%v8d)he-b_^@d*pqhq!#2p*a7*9e9h'

#: Turn this on if you need to debug Devilry
DEBUG = False
EXTJS4_DEBUG = DEBUG

#: Change this to the name of the system which you fetch data into Devilry from.
DEVILRY_SYNCSYSTEM = 'The Devilry demo syncsystem'

#: Url where users are directed when they do not have the permissions they believe they should have.
DEVILRY_LACKING_PERMISSIONS_URL = None

#: Url where users are directed when they want to know what to do if their personal info in Devilry is wrong.
DEVILRY_WRONG_USERINFO_URL = None

#: Deadline handling method:
#:
#:    0: Soft deadlines
#:    1: Hard deadlines
DEFAULT_DEADLINE_HANDLING_METHOD = 0
