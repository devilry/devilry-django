from .test import *  # noqa


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test',
        'USER': os.environ.get('PG_USER'),
        'PASSWORD': os.environ.get('PG_PASSWORD'),
        'PORT': '5435',  # Postgres 9.5,
        # 'PORT': '5436',  # Postgres 9.6,
        'HOST': '127.0.0.1',
    }
}
