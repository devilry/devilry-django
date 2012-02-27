.. _testsuite:

==========================
The devilry testsuite
==========================

Run **all** tests using::

    $ bin/django_dev.py test

Skip the *selenium* tests using::

    $ SKIP_SELENIUMTESTS=1 bin/django_dev.py test

Specify a browser for the selenium tests using (example uses Firefox)::

    $ SELENIUM_BROWSER=Firefox bin/django_dev.py test

*Chrome* is the default browser.
