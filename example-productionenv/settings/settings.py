from os.path import abspath, dirname, join
from devilry.defaults.settings import *

## Convenience to use paths relative to this file. With the magic below,
## PARENT_DIR is set to the productionenv directory. Some settings below use
## join(PARENT_DIR, 'something') to create OS-independent filesystem paths
## relative to productionenv. Feel free to use absolute paths instead
PARENT_DIR = dirname(dirname(abspath(__file__)))

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+g$%**q(w78xqa_2)(_+%v8d)he-b_^@d*pqhq!#2p*a7*9e9h'

## Where do we store files that students deliver?
# DELIVERY_STORE_ROOT = '/path/to/some/directory'
DELIVERY_STORE_ROOT = join(PARENT_DIR, 'deliverystore')

## You can dump related users into devilry. This setting is where the system
## tells users that this data comes from.
DEVILRY_SYNCSYSTEM = 'FS (Felles Studentsystem)'

## Nice to have this set to True while you are setting up devilry, however set
## it to False for production
DEBUG=True

## Example config for SQLite (see also PostgreSQL below)
DATABASES["default"] = {
    'ENGINE': 'django.db.backends.sqlite3',

    # Path to sqlite database file
    'NAME': join(PARENT_DIR, 'db.sqlite3')
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

## Settings required to work with server-conf/apache-vhost.conf
#DEVILRY_MAIN_PAGE='/devilry'
#DEVILRY_LOGOUT_URL='/devilry/authenticate/logout'
#LOGIN_URL='/devilry/authenticate/login'
#DEVILRY_STATIC_URL = '/devilry-static-files'
#DEVILRY_THEME_URL = '/devilry-static-files/theme/themes/devilry'
