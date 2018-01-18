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
    RQ_QUEUES = rq_setup.make_simple_rq_queue_setting(
        host='localhost',
        port=6379,
        db=0,
        password='secret'
    )



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
    $ venv/bin/python manage.py devilry_test_rq_task --queue default


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
