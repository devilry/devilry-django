from devilry.project.common.settings import *  # noqa
import urlparse

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

#####################################################
#
# Celery/Redis config
#
#####################################################
# redis_url_default = urlparse.urlparse(os.environ.get('REDIS_URL'))
#
# REDIS_URL_CONFIG = {
#     'port': redis_url_default.port,
#     'hostname': redis_url_default.hostname,
#     'password': redis_url_default.password,
#     'db_number': 0
# }
#
# BROKER_URL = 'redis://:{password}@{hostname}:{port}/{db_number}'.format(
#     password=REDIS_URL_CONFIG['password'],
#     hostname=REDIS_URL_CONFIG['hostname'],
#     port=REDIS_URL_CONFIG['port'],
#     db_number=REDIS_URL_CONFIG['db_number']
# )
#
# CELERY_RESULT_BACKEND = 'redis://:{password}@{hostname}:{port}/{db_number}'.format(
#     password=REDIS_URL_CONFIG['password'],
#     hostname=REDIS_URL_CONFIG['hostname'],
#     port=REDIS_URL_CONFIG['port'],
#     db_number=REDIS_URL_CONFIG['db_number']
# )
