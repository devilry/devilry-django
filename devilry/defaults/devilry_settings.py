"""
Defaults for settings defined by Devilry.
"""


# Make sure this does not end with / (i.e. '' means / is the main page).
# DEVILRY_MAIN_PAGE = '/django/devilry'
DEVILRY_MAIN_PAGE = ''

# The default grade-plugin:
DEVILRY_DEFAULT_GRADEEDITOR='asminimalaspossible'

DEVILRY_STATIC_URL = '/static' # Must not end in / (this means that '' is the server root)
DEVILRY_THEME_URL = DEVILRY_STATIC_URL + '/theme/themes/devilry'
#DEVILRY_EXTJS_URL = DEVILRY_STATIC_URL + '/extjshelpers/extjs'
DEVILRY_EXTJS_URL = 'http://cdn.sencha.io/ext-4.0.2a'
DEVILRY_LOGOUT_URL = '/authenticate/logout'
DEVILRY_HELP_URL = 'https://github.com/devilry/devilry-django/wiki/User-documentation'

#Set max file size to 5MB. Files greater than this size are split into chunks of this size.
DEVILRY_MAX_ARCHIVE_CHUNK_SIZE = 5000000

DEVILRY_SEND_EMAIL_TO_USERS = False
DEVILRY_EMAIL_SUBJECT_PREFIX_ADMIN = '[devilry-admin] '
DEVILRY_EMAIL_SIGNATURE = "This is a message from the Devilry assignment delivery system. " \
                  "Please do not respond to this email."

DEVILRY_DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsDeliveryStore'
DEVILRY_SYNCSYSTEM = 'YOUR MASTER SYSTEM HERE'


#################################################
# Settings without a default value
#################################################

## If we use django to serve static files, we need this setting to define
## where they are located. Static files are located in the devilry/static/
## directory in the devilry source repository.
#DEVILRY_STATIC_ROOT = '/path/to/static'

## The urlscheme+domain where devilry is located.
## DEVILRY_SCHEME_AND_DOMAIN+DEVILRY_MAIN_PAGE is the absolute URL to the devilry
## instance. WARNING: must not end with /
#DEVILRY_SCHEME_AND_DOMAIN = 'https://devilry.example.com'

## Email addresses
#DEVILRY_EMAIL_DEFAULT_FROM = 'devilry-support@example'
#DEVILRY_SYSTEM_ADMIN_EMAIL='devilry-support@example.com'
