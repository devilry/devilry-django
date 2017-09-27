#######################################
Setup the Celery background task server
#######################################

If you want to scale Devilry to more than a couple of hundred users, you really
have to configure the Celery background task server. Celery is installed by
default, but you need to configure a task broker. We recommend Redis.

Install Redis
=============
See https://redis.io/.


Configure Redis
===============
Uncomment the requirepass setting in redis.conf to set a password.
Remember to run Redis with this config::

    $ redis-server /path/to/redis.conf

You can tweak other configuration parameters in this file, such as port and other things,
so check it out.


Add Redis and Celery settings to Devilry
===========================================
Add the following to ``~/devilrydeploy/devilry_settings.py`` (change ``secret`` to
match the password in the redis.conf file) and set the correct config parameters in REDIS_CONFIG::

    REDIS_CONFIG = {
        'port': 6379,
        'hostname': 'localhost',
        'password': 'secret',
        'db_number': 0
    }

    BROKER_URL = 'redis://:{password}@{hostname}:{port}/{db_number}'.format(
        password='secret',
        hostname='localhost',
        port=6379,
        db_number=0
    )

    CELERY_RESULT_BACKEND = 'redis://:{password}@{hostname}:{port}/{db_number}'.format(
        password='secret',
        hostname='localhost',
        port=6379,
        db_number=0
    )

Run Celery
==========
To run Celery, use::

    $ cd ~/devilrydeploy/
    $ DJANGO_SETTINGS_MODULE=devilry_settings venv/bin/celery -A devilry.project.common worker -l debug

If this starts without any errors, Celery should be working. You can stop the
server using ``ctrl-c``. For all other cases than debugging and testing, we will be
running the Celery server via Supervisord (see :doc:`supervisord`).
