#####################
The devilry testsuite
#####################

Run **all** test::

    $ DJANGOENV=test python manage.py test devilry

Skip the *selenium* tests using::

    $ SKIP_SELENIUMTESTS=1 DJANGOENV=test python manage.py test

Specify a browser for the selenium tests using (example uses Firefox)::

    $ SELENIUM_BROWSER=Firefox DJANGOENV=test python manage.py test

*Chrome* is the default browser (configured in ``devilry.project.develop.settings.base``).


.. note::
    We use ``DJANGOENV=test python manage.py`` to run tests, because that makes
    ``manage.py`` use ``devilry.project.develop.settings.test``,
    which does not load Haystack or Celery.
