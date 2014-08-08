# We use this settings module when running senchatoolsbuild:
#
#    $ bin/django_dev.py senchatoolsbuild --buildall --settings settings.extjsbuild
#
#
# See the djangosenchatools docs (https://github.com/espenak/djangosenchatools)
# for details.

from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
EXTJS4_DEBUG = True
EXTJS4_DEBUGFILE = 'extjs4/ext-dev.js'
MIDDLEWARE_CLASSES += ['djangosenchatools.auth.SettingUserMiddleware']
AUTHENTICATION_BACKENDS = ('djangosenchatools.auth.SettingUserBackend',)
SENCHATOOLS_USER = 'grandma'
