from os.path import abspath, dirname, join

this_dir = dirname(abspath(__file__))

# If no admins are set, no emails are sent to admins
ADMINS = (
     ('Devilry admin', 'admin@example.com'),
)
MANAGERS = ADMINS

SEND_EMAIL_TO_USERS = False
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = join(this_dir, 'email_log')

EMAIL_SUBJECT_PREFIX = '[devilry] '
EMAIL_SUBJECT_PREFIX_ADMIN = '[devilry-admin] '

WEB_PAGE_PREFIX = 'http://devilry.ifi.uio.no/django/main'
EMAIL_DEFAULT_FROM = 'devilry-support@ifi.uio.no'
EMAIL_SIGNATURE = "This is a message from the Devilry assignment delivery system. " \
                  "Please do not respond to this email."

DEVILRY_SYSTEM_ADMIN_EMAIL='devilry-support@example.com'
