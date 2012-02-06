.. _testsuite:

==========================
The devilry testsuite
==========================

Run **all** tests using::

    $ bin/django_dev.py test

Skip the *selenium* tests using::

    $ SKIP_SELENIUM=1 bin/django_dev.py

Specify a browser for the selenium tests using (example uses Firefox)::

    $ SELENIUM_BROWSER=Firefox bin/django_dev.py

*Chrome* is the default browser.
