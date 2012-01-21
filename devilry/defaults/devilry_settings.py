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
DEVILRY_HELP_URL = 'https://github.com/devilry/devilry-django/wiki'

#Set max file size to 5MB. Files greater than this size are split into chunks of this size.
DEVILRY_MAX_ARCHIVE_CHUNK_SIZE = 5000000

DEVILRY_SEND_EMAIL_TO_USERS = True
DEVILRY_EMAIL_SUBJECT_PREFIX_ADMIN = '[devilry-admin] '
DEVILRY_EMAIL_SIGNATURE = "This is a message from the Devilry assignment delivery system. " \
                  "Please do not respond to this email."

DEVILRY_DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsHierDeliveryStore'
DEVILRY_FSHIERDELIVERYSTORE_INTERVAL = 1000
DEVILRY_SYNCSYSTEM = 'YOUR MASTER SYSTEM HERE'

## Email pattern. Set this, and add 'devilry.apps.autoset_empty_email_by_username' to INSTALLED_APPS
## to automatically set email to this pattern if it is not set when a user is saved.
#DEVILRY_DEFAULT_EMAIL_SUFFIX = '@example.com'

## When sorting by fullname, would you like to sort by last name? Currently
## only affects the overview over an entire period.
DEVILRY_SORT_FULL_NAME_BY_LASTNAME = True

## Messages that are displayed in the 3 dashboards for users with no permission to the dashboard
## The body of each message can contain html. For example, you can add an email link using: <a href="mailto:admin@example.com">admin@example.com</a>
DEVILRY_STUDENT_NO_PERMISSION_MSG = {'title': 'No published assignments',
                                     'body': 'You are not registered as a student on any assignments in Devilry. This is usually because you subject/course administrator has not published any assignments yet. Contact your subject/course administrator if this is wrong.'}
DEVILRY_EXAMINER_NO_PERMISSION_MSG = {'title': 'You are not an examiner',
                                      'body': 'You are not registered as an examiner on any publshed assignments in Devilry. If this is wrong, please contact the subject/course administrator.'}
DEVILRY_ADMINISTRATOR_NO_PERMISSION_MSG = {'title': 'You are not an administrator',
                                           'body': 'You are not registered as an administrator on any Node, Subject/Course, Period/Semester or Assignment in Devilry. If this is wrong, please contact the system administrator.'}



#################################################
# Settings without a default value
#################################################

## If we use django to serve static files, we need this setting to define
## where they are located. Static files are located in the devilry/static/
## directory in the devilry source repository.
#DEVILRY_STATIC_ROOT = '/path/to/static'
#DEVILRY_SYSTEM_ADMIN_EMAIL = 'devilry-support@example.com'
