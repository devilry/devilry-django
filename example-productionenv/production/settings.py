from os.path import abspath, dirname, join
from devilry.defaults.settings import *


# Make this unique, and don't share it with anybody.
SECRET_KEY = '+g$%**q(w78xqa_2)(_+%v8d)he-b_^@d*pqhq!#2p*a7*9e9h'

## Where do we store files that students deliver?
# DELIVERY_STORE_ROOT = '/path/to/some/directory'
DELIVERY_STORE_ROOT = join(dirname(abspath(__file__)), 'deliverystore') # This python magic sets it to the deliverystore/ directory subdirectory of the directory containing this config file.

## You can dump related users into devilry. This setting is where the system
## tells users that this data comes from.
DEVILRY_SYNCSYSTEM = 'FS (Felles Studentsystem)'

DEBUG=True

## Example config for SQLite
DATABASES["default"] = {
    'ENGINE': 'django.db.backends.sqlite3',

    # Path to sqlite database file
    ## This python magic sets the path to db.sqlite3 in the directory containing this config file
    'NAME': join(dirname(abspath(__file__)), 'db.sqlite3')
}



             #"postgres": {
                          #'ENGINE': 'postgresql_psycopg2',  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                          #'NAME': 'devilry',
                          #'USER': 'devilrydev',
                          #'PASSWORD': 'secret',
                          #'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
                          #'PORT': '',             # Set to empty string for default. Not used with sqlite3.
                         #}
