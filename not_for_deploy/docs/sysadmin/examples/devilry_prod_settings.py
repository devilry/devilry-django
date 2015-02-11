# Import the default settings from devilry
from devilry.project.production.settings import *


#: Turn this on if you need to debug Devilry
DEBUG = False
EXTJS4_DEBUG = DEBUG

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

# Make this 50 chars and RANDOM - do not share it with anyone
SECRET_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

#: Url where users are directed when they do not have the permissions they believe they should have.
DEVILRY_LACKING_PERMISSIONS_URL = None

#: Url where users are directed when they want to know what to do if their personal info in Devilry is wrong.
DEVILRY_WRONG_USERINFO_URL = None

#: Deadline handling method:
#:
#:    0: Soft deadlines
#:    1: Hard deadlines
DEFAULT_DEADLINE_HANDLING_METHOD = 0
