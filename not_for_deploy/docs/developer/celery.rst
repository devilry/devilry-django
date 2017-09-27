##############################################
Developing and testing Celery background tasks
##############################################


************************
How Celery is configured
************************
Celery_ is configured according to the `Celery first steps with Django`_ guide. The
app is in ``devilry.project.common.celery``, and it is imported as ``celery_app`` in
``devilry/project/common/__init__.py``.

For production, we leave the configuration up to sysadmins.

For development, we default to running Celery in eager mode, but we have commented out settings
in ``devilry.project.develop.develop`` for "real" Celery testing. Eager mode means that
all celery tasks runs in blocking mode in the current thread, so celery tasks runs just like any other
function.

For unit tests, we run Celery in eager mode (configured in ``devilry.project.develop.test``).


*****************************
Testing with non-eager Celery
*****************************

Install Redis
=============
See https://redis.io/. On Mac OSX, you can install Redis using Homebrew::

    $ brew install redis


Start the Redis server
======================
To start the redis server, run::

    $ redis-server

To stop the server, run::

    $ redis-server stop

To stop the server on OSX, run::

    $ redis-cli shutdown


Start the Celery worker
=======================
Run::

    $ celery -A devilry.project.common worker -l debug

It should print some info about the config, the tasks that it detects in Devilry,
and stop for input with the following message: ``celery@<your machine name> is ready``.


Try one of the test-tasks
==========================
Open the Django shell, and run one the test-tasks (while Redis and the Celery worker are both running)::

    $ python manage.py shell
    >>> from devilry.project.develop.tasks import add
    >>> result = add.delay(10, 20)
    >>> result.wait()
    30

If this works, Celery is configured correctly, and you should be able to see the job in
the terminal where the worker is running.


Things to remember
==================
(when running Celery tasks through the Celery worker)

- The output (stdout and stderr) goes to the Celery worker, not to runserver.
- You can get more verbose output from the worker with ``worker -l debug``.


Testing email sending with django-celery-email
==============================================

Uncomment the following lines in ``devilry.project.develop.settings.develop``::

    # INSTALLED_APPS += ['djcelery_email']
    # EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
    # CELERY_EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

And run the following in the Django shell:

    >>> from django.contrib.auth import get_user_model
    >>> from devilry.utils.devilry_email import send_message
    >>> send_message('Testsubject', 'Testmessage', get_user_model().objects.get(username='april'))



.. _Celery: http://celery.readthedocs.org/
.. _`Celery first steps with Django`: http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
