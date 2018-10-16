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
        'pyyaml==3.12',
        'Markdown==2.6.11',
        'Pygments==1.5',
        'flup==1.0.2',
        'gunicorn==19.9.0',
        'django-crispy-forms==1.6.0',
        'openpyxl==1.6.1',
        'django >= 1.11, < 1.12',
        # 'django==1.9.13',
        'URLObject==2.4.3',
        'django-simple-rest==1.4.1',
        'mimeparse==0.1.3',
        'django_errortemplates==1.0.1',
        'numpy==1.14.0',
        'anyjson==0.3.3',
        'rq==0.10.0',
        'django-rq==1.0.1',
        'redis==2.10.5',
        'python-dateutil==1.5',
        'pytz==2012j',
        'httplib2==0.7.7',
        'dj-static>=0.0.6',
        'dj-database-url>=0.3.0',
        'bleach==1.5.0',
        'html5lib==0.9999999',
        'psycopg2==2.7.3.2',
        'django_cradmin==1.2.3',
        'ievv_opensource==5.2.2',
        'arrow==0.12.0',
        'detektor==1.1.0-beta.012',
        'html2text==2018.1.9',
        'djangorestframework==3.8.2',
        # For django-allauth
        'django-allauth==0.36.0',
        'certifi==2017.11.5',
        'chardet==3.0.4',
        'idna==2.6',
        'oauthlib==2.0.6',
        'python-openid==2.2.5',
        'requests==2.18.4',
        'requests-oauthlib==0.8.0',
        'urllib3==1.22',
        'pycountry==17.9.23'
    ]
)
