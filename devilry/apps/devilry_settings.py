"""
Defaults for settings defined by Devilry.
"""


# Make sure this does not end with / (i.e. '' means / is the main page).
# DEVILRY_MAIN_PAGE = '/django/devilry'
DEVILRY_MAIN_PAGE = ''

# The default grade-plugin:
# grade_default:approvedgrade, grade_rstschema:rstschemagrade or grade_default:charfieldgrade
DEVILRY_DEFAULT_GRADEPLUGIN='grade_default:charfieldgrade'

DEVILRY_JQUERY_UI_THEME = 'devilry-blue'
DEVILRY_STATIC_URL = '/static'
DEVILRY_THEME_URL = DEVILRY_STATIC_URL + '/apps/theme/themes/devilry'
DEVILRY_EXTJS_URL = DEVILRY_STATIC_URL + '/ext-4.0.1'
DEVILRY_LOGOUT_URL = '/ui/logout'

#Set max file size to 5MB. Files greater than this size are split into chunks of this size.
DEVILRY_MAX_ARCHIVE_CHUNK_SIZE = 5000000

DEVILRY_SEND_EMAIL_TO_USERS = False
DEVILRY_EMAIL_SUBJECT_PREFIX_ADMIN = '[devilry-admin] '
DEVILRY_EMAIL_SIGNATURE = "This is a message from the Devilry assignment delivery system. " \
                  "Please do not respond to this email."

DEVILRY_DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsDeliveryStore'


#################################################
# Settings without a default value
#################################################

## If we use django to serve static files, we need this setting to define
## where they are located. Static files are located in the devilry/static/
## directory in the devilry source repository.
#DEVILRY_STATIC_ROOT = '/path/to/static'

## Email addresses
#DEVILRY_EMAIL_DEFAULT_FROM = 'devilry-support@example'
#DEVILRY_SYSTEM_ADMIN_EMAIL='devilry-support@example.com'
