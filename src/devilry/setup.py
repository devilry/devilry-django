from setuptools import setup, find_packages

setup(
    name = "devilry",
    version = "1.2.1.8",
    url = 'http://devilry.org',
    license = 'BSD',
    description = "A system for handling electronic deliveries.",
    author = 'The Devilry developers',
    packages = find_packages(),
    install_requires = ['setuptools', 'Django', 'Markdown', 'django_errortemplates',
                        'djangorestframework', 'Pygments',
                        'django-haystack',
                        'pysolr',
                        'httplib2',
                        #'flup',
                        #'PyYAML',
                        'django-celery',
                        'gunicorn']
)
