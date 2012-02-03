================================
The devilry test suite
================================

The tests that verifies the regular python code can be run using::

    $ bin/django_dev.py test -csetup.cfg -crun-all-tests.cfg


The tests that verifies the web interface (selenium tests)::

    $ bin/django_dev.py test -csetup.cfg -crun-all-seleniumtests.cfg
