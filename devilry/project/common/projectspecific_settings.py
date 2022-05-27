"""
Settings added for Devilry.
"""
import os


# Make sure this does not end with / (i.e. '' means / is the main page).
# DEVILRY_URLPATH_PREFIX = '/django/devilry'
DEVILRY_URLPATH_PREFIX = ''

# The default grade-plugin:
DEVILRY_DEFAULT_GRADEEDITOR = 'approved'

#: The directory where compressed archives are stored. Archives are compressed when examiners or students
#: downloads files from an assignment or a feedbackset.
DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY = None

DEVILRY_STATIC_URL = '/static'  # Must not end in / (this means that '' is the server root)
DEVILRY_MATHJAX_URL = 'https://cdn.mathjax.org/mathjax/latest/MathJax.js'
DEVILRY_LOGOUT_URL = '/authenticate/logout'
DEVILRY_HELP_URL = 'https://devilry.readthedocs.io/en/master/user/'
DEVILRY_CHANGELOG_URL = 'https://devilry.readthedocs.io/en/master/user/changelog_overview.html'


# Set max file size to 5MB. Files greater than this size are split into chunks of this size.
DEVILRY_MAX_ARCHIVE_CHUNK_SIZE = 5000000

DEVILRY_SEND_EMAIL_TO_USERS = True
DEVILRY_EMAIL_SUBJECT_PREFIX_ADMIN = '[devilry-admin] '
DEVILRY_EMAIL_SIGNATURE = \
    "This is a message from the Devilry assignment delivery system. "\
    "Please do not respond to this email."


DEVILRY_DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsHierDeliveryStore'
DEVILRY_FSHIERDELIVERYSTORE_INTERVAL = 1000
DEVILRY_EMAIL_DEFAULT_FROM = 'devilry-support@example.com'
DEVILRY_SYSTEM_ADMIN_EMAIL = 'devilry-admin@example.com'
DEVILRY_SCHEME_AND_DOMAIN = 'https://devilry.example.com'

DEVILRY_MESSAGE_RESEND_LIMIT = 2

# The name of the primary sync system where data is imported from.
# This is shown in the user interface, and can be a longer string
# with spaces.
DEVILRY_SYNCSYSTEM = 'YOUR SYNC SYSTEM HERE'

# The short name of the sync system that data is imported from.
# This can only contain english lower-case letters (a-z),
# numbers and ``_``.
DEVILRY_SYNCSYSTEM_SHORTNAME = 'x'

#: The default tag prefix used when importing tags from
#: from an external system.
DEVILRY_IMPORTED_PERIOD_TAG_DEFAULT_PREFIX = 'x'

#: Disable tests that require RQ to run.
DEVILRY_SKIP_RQ_TESTS = os.environ.get('DEVILRY_SKIP_RQ_TESTS', 'False') == 'True'

#: RQ email queue
DEVILRY_RQ_EMAIL_BACKEND_QUEUENAME = 'email'


#: If this is set, and the ``CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND``-setting
#: is ``False``, users will be assigned
#: ``<username><DEVILRY_DEFAULT_EMAIL_USERNAME_SUFFIX>`` as their primary email
#: address when they are created.
DEVILRY_DEFAULT_EMAIL_USERNAME_SUFFIX = None
# DEVILRY_DEFAULT_EMAIL_USERNAME_SUFFIX = 'example.com'


# DEVILRY_QUALIFIESFOREXAM_PLUGINS = [
#     'devilry_qualifiesforexam_approved.all',
#     'devilry_qualifiesforexam_approved.subset',
#     'devilry_qualifiesforexam_points',
#     'devilry_qualifiesforexam_select',
# ]

DEFAULT_DEADLINE_HANDLING_METHOD = 0

#: Maps devilryrole to assignment guidelines. What guidelines to show is matched using regex (re.fullmatch).
#:
#: Example::
#:
#:    DEVILRY_ASSIGNMENT_GUIDELINES = {
#:        'student': [
#:            (r'duck10.+', {
#:                '__default__': {
#:                    'htmltext': 'This is the assignment guidelines for inf10xx courses.',
#:                    'url': 'http://example.com'
#:                },
#:               'nb': {
#:                    'htmltext': 'Dette er retningslinjene for oppgaver i inf10xx kurs',
#:                    'url': 'http://example.com'
#:                }
#:            }),
#:            (r'duck11.+', {
#:                '__default__': {
#:                    'htmltext': 'This is the assignment guidelines for inf11xx courses.',
#:                    'url': 'http://example.com'
#:                },
#:                'nb': {
#:                    'htmltext': 'Dette er retningslinjene for oppgaver i inf11xx kurs',
#:                    'url': 'http://example.com'
#:                }
#:            })
#:        ]
#:    }
#:
#: You can test the regexes using ``python manage.py devilry_show_assignment_guidelines``.
DEVILRY_ASSIGNMENT_GUIDELINES = {}



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

#: The number of minutes to delay publishing an assignment after it is created.
#: This is also the minimum amount of time between the current time and
#: the first deadline.
DEVILRY_ASSIGNMENT_PUBLISHING_TIME_DELAY_MINUTES = 60 * 6


#: If this is ``True``, we enable an upload directory structure that scales
#: to a lot of files on filesystems with limits on files per directory.
#: Normally needed if you are using a traditional filesystem, but not for
#: blob storage filesystems like AWS S3.
DEVILRY_RESTRICT_NUMBER_OF_FILES_PER_DIRECTORY = False


#: If this is set to a value, we extract a prettier shortname for a user
#: than "feide:myname@mydomain.no" for the provided suffix.
#:
#: I.E.: If you set this to "uio.no", University of Oslo users that
#: authenticate with Feide will get their UiO username as their shortname.
#:
#: It is **very dangerous to change this value after you have users in the database**
#: because it can lead to users getting access to other users accounts.
#: Lets say two different users with ID ``feide:peter@test1.com`` and ``feide:peter@test2.com``
#: exists in Dataporten. If you first set this setting to ``@test1.com``, and
#: later change this setting to ``test2.com``, the peter from test2.com will gain
#: access to the Devilry account for the peter from test1.com!
DEVILRY_FEIDE_USERID_SEC_TO_USERNAME_SUFFIX = None


#: If this is set to a value, we will use this as the favicon.
DEVILRY_BRANDING_FAV_ICON_PATH = None


############################################################################
#
# Hard deadlines info box message for feed.
#
# This is a info message that will appear in the top of the feed if hard
# deadlines are enabled for an assignment. You can add different translations
# of this message by adding a ISO 639-1 code mapped to a message.
#
# Example:
# DEVILRY_HARD_DEADLINE_INFO_FOR_STUDENTS = {
#   ...,
#   'en': 'This assignment uses hard deadlines...'
# }
#
# Note:
#   The '__default' is in english and is marked for translation.
#   You may override this, but it should be in a language that all the users
#   understand.
#
#############################################################################
gettext_noop = lambda s: s


#: Hard deadline info texts for students.
DEVILRY_HARD_DEADLINE_INFO_FOR_STUDENTS = {
    '__default': gettext_noop('This assignment uses hard deadlines. You will not be able to write comments '
                              'or upload files after the deadline has expired.')
}

#: Hard deadline info texts for examiners and admins
DEVILRY_HARD_DEADLINE_INFO_FOR_EXAMINERS_AND_ADMINS = {
    '__default': gettext_noop('This assignment uses hard deadlines. Students will not be able to write comments '
                              'or upload files after the deadline has expired.')
}


############################################################
#
# Comment edit history settings.
#
# We provide a few settings for what students should be able
# to see about comment edits.
#
#
############################################################

#: Can students edit their comments?
#: Students can always see their own comment edit history, but this will of course not
#: available unless they have or have had the ability to edit their comments.
DEVILRY_COMMENT_STUDENTS_CAN_EDIT = os.environ.get(
    'DEVILRY_COMMENT_STUDENTS_CAN_EDIT', 'True') == 'True'

#: Should students be able to see the comment edit history of other users in their group?
#: Students only see comments or comment edit histories that are visible to everyone. This means that
#: students can only see edit history entries for comments that where had the "visible to everyone" state when the
#: edit history entry was created.
DEVILRY_COMMENT_STUDENTS_CAN_SEE_OTHER_USERS_COMMENT_HISTORY = os.environ.get(
    'DEVILRY_COMMENT_STUDENTS_CAN_SEE_OTHER_USERS_COMMENT_HISTORY', 'True') == 'True'
