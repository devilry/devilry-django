#######################################
Setup the Celery background task server
#######################################

If you want to scale Devilry to more than a couple of hundred users, you really
have to configure the Celery background task server. Celery is installed by
default, but you need to configure a task broker. We recommend RabbitMQ.

Install RabbitMQ
================
Follow the guides at their website: http://www.rabbitmq.com/download.html.

Refer to the RabbitMQ docs for regular configuration, like logging and
database-file location. The defaults are usable.


Configure RabbitMQ for Devilry
==============================
Start the RabbitMQ server.

RabbitMQ creates a default admin user named ``guest`` with password ``guest``.
Remove the guest user, and create a new admin user (use another password than
``secret``)::

    $ rabbitmqctl delete_user guest
    $ rabbitmqctl add_user admin secret
    $ rabbitmqctl set_user_tags admin administrator
    $ rabbitmqctl set_permissions admin ".*" ".*" ".*"

Setup a vhost for Devilry with a username and password (use another password
than ``secret``)::

    $ rabbitmqctl add_user devilry secret
    $ rabbitmqctl add_vhost devilryhost
    $ rabbitmqctl set_permissions -p devilryhost devilry ".*" ".*" ".*"


Add RabbitMQ and Celery settings to Devilry
===========================================
Add the following to ``~/devilrydeploy/devilry_settings.py`` (change ``secret`` to
match your password)::

    CELERY_ALWAYS_EAGER = False
    BROKER_URL = 'amqp://devilry:secret@localhost:5672/devilryhost'
    CELERY_RESULT_BACKEND = BROKER_URL

Run Celery
==========
To run Celery, use::

    $ cd ~/devilrydeploy/
    $ DJANGO_SETTINGS_MODULE=devilry_settings venv/bin/celery -A devilry.project.common worker -l debug

If this starts without any errors, Celery should be working. You can stop the
server using ``ctrl-c``. For all other cases than debugging and testing, we will be
running the Celery server via Supervisord (see :doc:`supervisord`).
