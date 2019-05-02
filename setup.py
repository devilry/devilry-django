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
    author=('Tor Johansen, Espen Angell Kristiansen, Bendik Opstad, Vegard Angell, '
            'Magne Westlie, Ilya Kostolomov, Christian Tryti, Rebekka M\u00F8rken, Stian Julseth'),
    author_email='devilry-contact@googlegroups.com',
    include_package_data=True,
    description="A system for handling electronic deliveries. See https://github.com/devilry/devilry-django.",
    packages=find_packages(exclude=["devilry_rest"]),
    install_requires=[
        'setuptools',
        'pyyaml==3.13',
        'Markdown==2.6.11',
        'Pygments==2.0',
        'flup==1.0.3',
        'gunicorn==19.9.0',
        'django-crispy-forms==1.7.2',
        'openpyxl==1.6.1',
        'django==2.1.7',
        # 'django==2.0.13',
        # 'django==1.11.20',
        # 'django==1.9.13',
        'URLObject==2.4.3',
        # 'django-simple-rest==1.4.1',
        'mimeparse==0.1.3',
        'django_errortemplates==1.0.1',
        'numpy==1.14.0',
        'anyjson==0.3.3',
        'rq==0.13.0',
        'django-rq==1.3.0',
        'redis==3.0.1',
        'python-dateutil==2.8',
        'pytz==2018.9',
        'httplib2==0.7.7',
        'dj-static>=0.0.6',
        'dj-database-url>=0.3.0',
        'bleach==1.5.0',
        'html5lib==0.9999999',
        'psycopg2==2.7.3.2',
        'cradmin_legacy>=1.3.0a0',
        'ievv_opensource==5.14.2',
        'xlsxwriter==1.1.2',
        'arrow==0.12.0',
        'detektor==1.1.0-beta.012',
        'html2text==2018.1.9',
        'djangorestframework==3.8.2',
        # For django-allauth
        'django-allauth==0.37.0',
        'certifi==2017.11.5',
        'chardet==3.0.4',
        'idna==2.6',
        'oauthlib==2.0.6',
        'python-openid==2.2.5',
        'requests==2.19.1',
        'requests-oauthlib==0.8.0',
        'urllib3==1.22',
        'pycountry==17.9.23'
    ]
)
