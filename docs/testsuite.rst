.. _testsuite:

==========================
The devilry testsuite
==========================

Run **all** (see  tests using::

    $ bin/django_dev.py test

Skip the *selenium* tests using::

    $ SKIP_SELENIUMTESTS=1 bin/django_dev.py test

Specify a browser for the selenium tests using (example uses Firefox)::

    $ SELENIUM_BROWSER=Firefox bin/django_dev.py test

*Chrome* is the default browser.




The testsuite runner, and how we exclude/include tests
======================================================

We use a custom testsuiterunner, ``devilry_settings.testsuiterunner.FilterableTestSuiteRunner``.
This runner uses fnmatch (shell patterns) to exclude and include testcases. Excludes and
includes are configured in the ``TEST_FILTER``-setting, and the defaults are configured in
``devilry_settings.default_settings.TEST_FILTER``. The patterns matches against the full
python path to each testcase (the module path + the class name + method name).

When you specify a testcase or app manually, ``TEST_FILTER`` is ignored. So you can, for example,
still run the djangorestframework tests with::

    $ bin/django_dev.py test djangorestframework

even if it is excluded in ``TEST_FILTER``.


See ignored testcases
---------------------

Run tests with ``-v3`` to list ignored apps::

    $ bin/django_dev.py test -v3

Each ignored test is listed like this::

    [TESTSUITE DEBUG] Ignored 'djangorestframework.tests.renderers.RendererIntegrationTests.test_bla'