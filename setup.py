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
        'django-crispy-forms==1.10.0',
        'openpyxl==1.6.1',
        'django==3.1.*',
        'URLObject==2.4.3',
        'mimeparse==0.1.3',
        'django_errortemplates==1.0.1',
        'numpy==1.19.*',
        'anyjson==0.3.3',
        'rq==1.8.0',
        'django-rq==2.4.1',
        'redis==3.5.3',
        'python-dateutil==2.8',
        'pytz==2018.9',
        'httplib2==0.7.7',
        'dj-static>=0.0.6',
        'dj-database-url>=0.3.0',
        'html5lib==0.9999999',
        'psycopg2==2.8.6',
        'django_cradmin==8.0.2',
        'cradmin_legacy>=3.1.0,<4.0.0',
        'ievv_opensource>=7.0.3,<8.0.0',
        'xlsxwriter==1.1.2',
        'arrow==0.12.0',
        'detektor==1.1.0-beta.012',
        'html2text==2018.1.9',
        'djangorestframework==3.12.4',
        # For django-allauth
        'django-allauth==0.42.*',
        'certifi==2017.11.5',
        'chardet==3.0.4',
        'idna==2.6',
        'oauthlib==2.0.6',
        'python-openid==2.2.5',
        'requests==2.19.1',
        'requests-oauthlib==0.8.0',
        'urllib3==1.22',
        'pycountry==17.9.23',
        'six==1.15.0'
    ]
)
