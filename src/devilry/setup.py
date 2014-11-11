from setuptools import setup, find_packages

setup(
    name = "devilry",
    version = "1.4.9",
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
                        'South',
                        #'flup',
                        #'PyYAML',
                        'django-celery',
                        'mock',
                        'devilry_rest', # NOTE: We only need this until all modules importing from ``devilry.utils.rest*`` is updated
                        'gunicorn']
)
