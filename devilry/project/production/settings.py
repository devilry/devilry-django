import urlparse
from devilry.project.common.settings import *  # noqa

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

redis_url_default = urlparse.urlparse(os.environ.get('REDIS_URL'))

REDIS_URL_CONFIG = {
    'port': redis_url_default.port,
    'hostname': redis_url_default.hostname,
    'username': redis_url_default.username
    'password': redis_url_default.password,
}

BROKER_URL = 'redis://{username}:{password}@{hostname}:{port}'.format(
    username=REDIS_URL_CONFIG['username'],
    password=REDIS_URL_CONFIG['password'],
    hostname=REDIS_URL_CONFIG['hostname'],
    port=REDIS_URL_CONFIG['port']
)

CELERY_RESULT_BACKEND = 'redis://{username}:{password}@{hostname}:{port}'.format(
    username=REDIS_URL_CONFIG['username'],
    password=REDIS_URL_CONFIG['password'],
    hostname=REDIS_URL_CONFIG['hostname'],
    port=REDIS_URL_CONFIG['port']
)