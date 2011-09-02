"""
Defaults for settings defined by Devilry.
"""


# Make sure this does not end with / (i.e. '' means / is the main page).
# DEVILRY_URLPATH_PREFIX = '/django/devilry'
DEVILRY_URLPATH_PREFIX = ''

# The default grade-plugin:
DEVILRY_DEFAULT_GRADEEDITOR='approved'

DEVILRY_STATIC_URL = '/static' # Must not end in / (this means that '' is the server root)
DEVILRY_THEME_URL = DEVILRY_STATIC_URL + '/theme/themes/devilry'
DEVILRY_EXTJS_URL = DEVILRY_STATIC_URL + '/extjshelpers/extjs'
#DEVILRY_EXTJS_URL = 'http://cdn.sencha.io/ext-4.0.2a'
DEVILRY_MATHJAX_URL = 'https://d3eoax9i5htok0.cloudfront.net/mathjax/latest/MathJax.js'
DEVILRY_LOGOUT_URL = '/authenticate/logout'
DEVILRY_HELP_URL = 'https://github.com/devilry/devilry-django/wiki/User-documentation'

#Set max file size to 5MB. Files greater than this size are split into chunks of this size.
DEVILRY_MAX_ARCHIVE_CHUNK_SIZE = 5000000

DEVILRY_SEND_EMAIL_TO_USERS = True
DEVILRY_EMAIL_SUBJECT_PREFIX_ADMIN = '[devilry-admin] '
DEVILRY_EMAIL_SIGNATURE = "This is a message from the Devilry assignment delivery system. " \
                  "Please do not respond to this email."

DEVILRY_DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsDeliveryStore'
DEVILRY_SYNCSYSTEM = 'YOUR MASTER SYSTEM HERE'



## These 3 can contain html. For example, you can add an email link using: <a href="mailto:admin@example.com">admin@example.com</a>
DEVILRY_STUDENT_NO_PERMISSION_MSG = 'You are not registered as a student on anything in Devilry. If this is wrong, please contact the system administrator.'
DEVILRY_EXAMINER_NO_PERMISSION_MSG = 'You are not registered as an examiner on anything in Devilry. If this is wrong, please contact the system administrator.'
DEVILRY_ADMINISTRATOR_NO_PERMISSION_MSG = 'You are not registered as an administrator on anything in Devilry. If this is wrong, please contact the system administrator.'


#################################################
# Settings without a default value
#################################################

## If we use django to serve static files, we need this setting to define
## where they are located. Static files are located in the devilry/static/
## directory in the devilry source repository.
#DEVILRY_STATIC_ROOT = '/path/to/static'
#DEVILRY_SYSTEM_ADMIN_EMAIL = 'devilry-support@example.com'
