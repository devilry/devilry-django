# Use this settings module with runserver when running senchatoolsbuild:
#
#    $ bin/django_dev.py senchatoolsbuild --buildall --settings settings.extjsbuild
#
#
# See the djangosenchatools docs (https://github.com/espenak/djangosenchatools)
# for details.

from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
EXTJS4_DEBUG = True
MIDDLEWARE_CLASSES += ['djangosenchatools.auth.SettingUserMiddleware']
AUTHENTICATION_BACKENDS = ('djangosenchatools.auth.SettingUserBackend',)
SENCHATOOLS_USER = 'grandma'
