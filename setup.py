import json
from setuptools import setup, find_packages

with open('devilry/version.json') as versionfile:
    version = json.load(versionfile)


setup(
    name="devilry",
    version=version,
    url='http://devilry.org',
    license='BSD',
    zip_safe=False,
    author=(u'Tor Johansen, Espen Angell Kristiansen, Bendik Opstad, Vegard Angell, '
            u'Magne Westlie, Ilya Kostolomov, Christian Tryti, Rebekka M\u00F8rken, Stian Julseth'),
    author_email='devilry-contact@googlegroups.com',
    include_package_data=True,
    description="A system for handling electronic deliveries. See https://github.com/devilry/devilry-django.",
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'pyyaml==3.10',
        'Markdown==2.3.1',
        'Pygments==1.5',
        'flup==1.0.2',
        'gunicorn==19.2.1',
        'django-crispy-forms==1.6.0',
        'openpyxl==1.6.1',
        'django==1.9.9',
        'URLObject==2.4.3',
        'django-simple-rest==1.4.1',
        'mimeparse==0.1.3',
        'django_errortemplates==1.0.1',
        'numpy==1.6.2',
        'amqp==1.4.9',
        'anyjson==0.3.3',
        'billiard==3.3.0.23',
        'celery==3.1.23',
        'kombu==3.0.34',
        'python-dateutil==1.5',
        'pytz==2012j',
        'django-celery-transactions==0.2.0',
        'httplib2==0.7.7',
        'detektor==1.1.0-beta.012',
        'dj-static>=0.0.6',
        'dj-database-url>=0.3.0',
        'bleach==1.5.0',
        'html5lib==0.9999999',
        'psycopg2==2.7.3.2',
        'django_cradmin==1.1.1',
        'ievv_opensource==4.1.0',
        'arrow==0.10.0',

        # For django-allauth
        'django-allauth==0.34.0',
        'certifi==2017.11.5',
        'chardet==3.0.4',
        'idna==2.6',
        'oauthlib==2.0.6',
        'python-openid==2.2.5',
        'requests==2.18.4',
        'requests-oauthlib==0.8.0',
        'urllib3==1.22',
    ]
)
