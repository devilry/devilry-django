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
            u'Magne Westlie, Ilya Kostolomov, Christian Tryti, Rebekka M\u00F8rken'),
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
        'django-extjs4==1.1.4-extjs4.1.1',
        'gunicorn==0.17.2',
        'django-crispy-forms==1.4.0',
        'openpyxl==1.6.1',
        'django==1.6.5',
        'URLObject==2.0.1',
        'django-simple-rest==1.4.1',
        'mimeparse==0.1.3',
        'django_errortemplates==1.0.1',
        'numpy==1.6.2',
        'amqp==1.4.6',
        'anyjson==0.3.3',
        'billiard==3.3.0.19',
        'celery==3.1.17',
        'kombu==3.0.37',
        'python-dateutil==1.5',
        'pytz==2012j',
        'django-celery-transactions==0.2.0',
        'django-haystack==2.3.1',
        'httplib2==0.7.7',
        'South==1.0.0',
        'detektor==1.1.0-beta.012',
        'djangorestframework==0.3.3',
        'django_cradmin==1.0.0-b18',
        'dj-static>=0.0.6',
        'dj-database-url>=0.3.0'
    ]
)
