from os.path import abspath, dirname, join

# Import the default settings from devilry
from devilry.defaults.settings import *

## Convenience variable to use paths relative to this file. With the magic below,
## parent_dir is set to the parentdirectory of the directory containing _this_ file.
## Some settings below use join(parent_dir, 'something') to create
## OS-independent filesystem paths relative to parent_dir.
## Feel free to use absolute paths instead
parent_dir = dirname(dirname(abspath(__file__)))

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+g$%**q(w78xqa_2)(_+%v8d)he-b_^@d*pqhq!#2p*a7*9e9h'

## Where do we store files that students deliver?
DEVILRY_FSHIERDELIVERYSTORE_ROOT = join(parent_dir, 'deliverystore')

## You can dump related users into devilry. This setting is where the system
## tells users that this data comes from.
DEVILRY_SYNCSYSTEM = 'FS (Felles Studentsystem)'

## Nice to have this set to True while you are setting up devilry, however set
## it to False for production
DEBUG = True



#############################################
# Configure the database
#############################################
DATABASES = {}

## Example config for SQLite (see also PostgreSQL below)
DATABASES["default"] = {
    'ENGINE': 'django.db.backends.sqlite3',

    # Path to sqlite database file
    'NAME': join(parent_dir, 'db.sqlite3')
}

## Example config for PostgreSQL
#DATABASES["default"] = {
#    'ENGINE': 'django.db.backends.postgresql_psycopg2',
#    'NAME': 'devilry', # Name of the database
#    'USER': 'devilryuser', # Database user
#    'PASSWORD': 'secret', # Password of database user
#    'HOST': '', # Set to empty string for localhost.
#    'PORT': '', # Set to empty string for default.
#}




#######################################################
# Email
# - The default is to "send" emails to a directory. This is useful when
#   checking if email works, however you should change it to SMTP in production
#######################################################

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = join(parent_dir, 'email_log')

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.example.com'
#EMAIL_PORT = 25

## Email addresses
DEVILRY_EMAIL_DEFAULT_FROM = 'devilry-support@example.com'
DEVILRY_SYSTEM_ADMIN_EMAIL = 'devilry-support@example.com'

## The urlscheme+domain where devilry is located. Used when sending links to users via email.
## DEVILRY_SCHEME_AND_DOMAIN+DEVILRY_URLPATH_PREFIX is the absolute URL to the devilry
## instance. WARNING: must not end with /
DEVILRY_SCHEME_AND_DOMAIN = 'https://devilry.example.com'



###########################################
# Logging - These defaults are usually enough
# - The default config logs to the ``log/`` subdir of the directory containing
#   _this_ file.
###########################################
from devilry.defaults.log import create_logging_config
logdir = join(parent_dir, 'log')
LOGGING = create_logging_config(
                                # Send error log messages to ADMINS on email?
                                mail_admins=True,

                                # Log to file? Logs are placed in the directory
                                # configured by log_to_file_dir
                                log_to_file=True,
                                log_to_file_dir=logdir,

                                # Log to stderr?
                                log_to_stderr=False,

                                # Set this to WARN to only log very dangerous
                                # actions, to INFO to log any dangerous action,
                                # or to ERROR to only log errors.
                                dangerous_actions_loglevel='INFO'
                               )

