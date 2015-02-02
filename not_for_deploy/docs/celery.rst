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
TODO


.. _Celery: http://celery.readthedocs.org/
.. _`Celery first steps with Django`: http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
