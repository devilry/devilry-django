"""
Settings added for Devilry.
"""


# Make sure this does not end with / (i.e. '' means / is the main page).
# DEVILRY_URLPATH_PREFIX = '/django/devilry'
DEVILRY_URLPATH_PREFIX = ''

# The default grade-plugin:
DEVILRY_DEFAULT_GRADEEDITOR = 'approved'

#: Where to store zipfiles for filedownloads
DEVILRY_GROUP_ZIPFILE_DIRECTORY = None

DEVILRY_STATIC_URL = '/static'  # Must not end in / (this means that '' is the server root)
DEVILRY_MATHJAX_URL = 'https://cdn.mathjax.org/mathjax/latest/MathJax.js'
DEVILRY_LOGOUT_URL = '/authenticate/logout'
DEVILRY_HELP_URL = 'https://devilry-userdoc.readthedocs.org'

# Set max file size to 5MB. Files greater than this size are split into chunks of this size.
DEVILRY_MAX_ARCHIVE_CHUNK_SIZE = 5000000

DEVILRY_SEND_EMAIL_TO_USERS = True
DEVILRY_EMAIL_SUBJECT_PREFIX_ADMIN = '[devilry-admin] '
DEVILRY_EMAIL_SIGNATURE = \
    "This is a message from the Devilry assignment delivery system. "\
    "Please do not respond to this email."

DEVILRY_DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsHierDeliveryStore'
DEVILRY_FSHIERDELIVERYSTORE_INTERVAL = 1000
DEVILRY_SYNCSYSTEM = 'YOUR SYNC SYSTEM HERE'
DEVILRY_SYNCSYSTEM_TAG_PREFIX = 'x'
DEVILRY_EMAIL_DEFAULT_FROM = 'devilry-support@example.com'
DEVILRY_SYSTEM_ADMIN_EMAIL = 'devilry-admin@example.com'
DEVILRY_SCHEME_AND_DOMAIN = 'https://devilry.example.com'

#: If this is False, we disable features that require background processing,
#: such as search.
DEVILRY_ENABLE_CELERY = True


#: If this is set, and the ``DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND``-setting
#: is ``False``, users will be assigned
#: ``<username><DEVILRY_DEFAULT_EMAIL_USERNAME_SUFFIX>`` as their primary email
#: address when they are created.
# DEVILRY_DEFAULT_EMAIL_USERNAME_SUFFIX = 'example.com'
DEVILRY_DEFAULT_EMAIL_USERNAME_SUFFIX = None


# DEVILRY_QUALIFIESFOREXAM_PLUGINS = [
#     'devilry_qualifiesforexam_approved.all',
#     'devilry_qualifiesforexam_approved.subset',
#     'devilry_qualifiesforexam_points',
#     'devilry_qualifiesforexam_select',
# ]

#: Deadline handling method:
#:
#:    0: Soft deadlines
#:    1: Hard deadlines
DEFAULT_DEADLINE_HANDLING_METHOD = 0


#: Url where users are directed when they do not have the permissions they believe they should have.
DEVILRY_LACKING_PERMISSIONS_URL = None

#: Url where users are directed when they want to know what to do if their personal info in Devilry is wrong.
DEVILRY_WRONG_USERINFO_URL = None

#: The URL of the official help pages for Devilry.
DEVILRY_OFFICIAL_HELP_URL = 'http://devilry.org#help'

#: Url where users can go to get documentation for Devilry that your organization provides.
DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_URL = None

#: Text for the DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_URL link.
DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_TEXT = None

#: The documentation version to use.
DEVILRY_DOCUMENTATION_VERSION = 'latest'

#: A Django template to include at the top of the frontpage (below the navbar, but above the main content).
DEVILRY_FRONTPAGE_HEADER_INCLUDE_TEMPLATE = None

#: A Django template to include at the bottom of the frontpage.
DEVILRY_FRONTPAGE_FOOTER_INCLUDE_TEMPLATE = None

#: A Django template to include at the top of the help page (below the navbar, but above the main content).
DEVILRY_HELP_PAGE_HEADER_INCLUDE_TEMPLATE = None

#: A Django template to include at the bottom of the help page.
DEVILRY_HELP_PAGE_FOOTER_INCLUDE_TEMPLATE = None

#: A Django template to include at the top of the profile page (below the navbar, but above the main content).
DEVILRY_PROFILEPAGE_HEADER_INCLUDE_TEMPLATE = None

#: A Django template to include at the bottom of the profile page.
DEVILRY_PROFILEPAGE_FOOTER_INCLUDE_TEMPLATE = None

#: Enable/disable creating zip-files on demand. This requires a traditional
#: file system.
DEVILRY_ENABLE_REALTIME_ZIPFILE_CREATION = True

#: Django apps that override the Devilry javascript translations (which is most
#: of the Devilry user interface).
DEVILRY_JAVASCRIPT_LOCALE_OVERRIDE_APPS = tuple()

#: Enable MathJax?
DEVILRY_ENABLE_MATHJAX = True

#: The number of minutes to delay publishing an assignment after it is created.
#: This is also the minimum amount of time between the current time and
#: the first deadline.
DEVILRY_ASSIGNMENT_PUBLISHING_TIME_DELAY_MINUTES = 60 * 6
