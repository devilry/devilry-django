import os

"""
A simple Django settings module proxy that lets us configure Django
using the DJANGOENV environment variable.

Example (running tests)::

    $ DJANGOENV=test python manage.py test

Defaults to the ``develop`` enviroment, so developers can use ``python
manage.py`` without anything extra during development.
"""

DJANGOENV = os.environ.get('DJANGOENV', 'develop')

if DJANGOENV == 'develop':  # Used for local development
    from devilry.project.develop.settings.develop import *
elif DJANGOENV == 'postgres_develop':  # Used for local development with Postgres
    from devilry.project.develop.settings.postgres_develop import *
elif DJANGOENV == 'test':  # Used when running the Django tests
    from devilry.project.develop.settings.test import *
elif DJANGOENV == 'postgres_test':  # Used when running the Django tests with Postgres
    from devilry.project.develop.settings.test import *
elif DJANGOENV == 'extjsbuild':  # Used when building extjs apps
    from devilry.project.develop.settings.extjsbuild import *
elif DJANGOENV == 'noextjsdebug':  # Used to develop/try the UI with built ExtJS apps
    from devilry.project.develop.settings.noextjsdebug import *
else:
    raise ValueError('Invalid value for the DJANGOENV environment variable: {!r}'.format(DJANGOENV))
