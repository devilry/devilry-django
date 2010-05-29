# Overrides the required settings to run using mod_wsgi as configured
# in ../wsgi/example.wsgi


from settings import *

DEVILRY_MAIN_PAGE = '/django/example/'
LOGIN_URL = '/django/example/ui/login'
DEVILRY_RESOURCES_URL = '/devilry-resources'
ADMIN_MEDIA_PREFIX = DEVILRY_RESOURCES_URL + '/superadminmedia/'
