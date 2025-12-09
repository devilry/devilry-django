##################################################
Setup Redis with RQ for background task processing
##################################################

If you want to scale Devilry to more than a couple of hundred users, you
have to configure the RQ and Redis. RQ is installed by
default, but you need to configure a task broker. We recommend Redis.

Install Redis
=============
See https://redis.io/.


Configure Redis
===============
Uncomment the ``requirepass`` setting in redis.conf to set a password.
Remember to run Redis with this config, it is not loaded by default::

    $ redis-server /path/to/redis.conf

You can tweak other configuration parameters in this file, such as port and other things,
so check it out.


Add RQ setup for Redis Devilry
==============================
Add the following to ``~/devilrydeploy/devilry_settings.py`` (change ``secret`` to
match the password in the redis.conf file) and set the correct config parameters for Redis to the RQ-queues::

    #: Setup Redis connection settings for background task server.
    from devilry.utils import rq_setup
    RQ_QUEUES = rq_setup.make_simple_rq_queue_setting(
        host='localhost',
        port=6379,
        db=0,
        password='secret'
    )


For more complex setup, like redis-sentinel etc., you need to setup
RQ_QUEUES manually with ``default``, ``email``, and ``highpriority``
queues. Skeleton::

    RQ_QUEUES = {
        'default': {
            # options
        },
        'email': {
            # options
        },
        'highpriority': {
            # options
        },
    }

Refer to the README for https://github.com/rq/django-rq for details about the
available options.


Run RQ workers
==============
To run RQ workers, use::

    $ cd ~/devilrydeploy/
    $ venv/bin/python manage.py rqworker default email highpriority

Alternatively you can run one RQ worker for each queue::

    $ cd ~/devilrydeploy/
    $ venv/bin/python manage.py rqworker default
    $ venv/bin/python manage.py rqworker email
    $ venv/bin/python manage.py rqworker highpriority


Verifying the setup
===================
You can verify the setup by running the ``devilry_test_rq_task`` management command::

    $ cd ~/devilrydeploy/
    $ venv/bin/python manage.py devilry_test_rq_task success --queue default

You may also want to check that errors are handled correctly::

    $ cd ~/devilrydeploy/
    $ venv/bin/python manage.py devilry_test_rq_task fail --queue default
    $ venv/bin/python manage.py devilry_test_rq_task crash --queue default

The `fail` task will report a handled exception, while the `crash` task will
simulate a worker crash. Check the logs of the RQ worker to verify that the
errors are logged correctly. If you have setup a custom `DEVILRY_ERROR_REPORTER_CLASS`,
the `fail` task will be reported according to the error reporter class.
The `fail` task can also take a `--userid` argument to simulate errors
for specific users. This is only useful if the `DEVILRY_ERROR_REPORTER_CLASS`
is setup to report user information (e.g.: SentryErrorReporter).

Furthermore, we have the `DEVILRY_DEBUG_ERROR_TRIGGER_USER_SHORTNAMES` setting that you
can use to trigger errors for specific users. This is useful to verify that
error reporting is working as expected for real tasks in Devilry. This is triggered
by adding the `shortname` of users to the `DEVILRY_DEBUG_ERROR_TRIGGER_USER_SHORTNAMES` list
in settings::

    DEVILRY_DEBUG_ERROR_TRIGGER_USER_SHORTNAMES = ['myshortname1', 'myshortname2']

You can then trigger errors by:

- Creating a compressed file (download feedbackset) as one of the users in the list.
- Triggering message sending (e.g.: add a comment to an assignment) where one of the users in the list is
  a recipient of the message.

.. warning:: Make sure you restart the RQ workers AND the web workers after changing this setting.

.. note:: You can find the `shortname` of users in the admin/superuser interface on the users page.


Advanced setup
==============
For full documentation for RQ_QUEUES setting, see https://github.com/rq/django-rq .
Just make sure you set up the config for these qeueues:

- default
- email
- highpriority

.. warning::
    Devilry updates may add more required queues. Be aware that custom
    tuning the RQ_QUEUES setting may break your setup when you update Devilry.
