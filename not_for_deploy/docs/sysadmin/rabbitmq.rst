################
Install RabbitMQ
################

If you want to scale Devilry to more than a couple of hundred users, you really
have to configure the Celery background task server. Celery is installed by
default, but you need to configure a task broker. We recommend RabbitMQ.

.. note::

    You can avoid configring background tasks for now if you are just testing
    Devilry, or are using it on a very small amount of users. Simply skip this
    section of the guide, and configure::

        CELERY_ALWAYS_EAGER = True

    in ``devilry_prod_settings.py``. Note that this will make all background
    tasks, like search index updates and email sending run in realtime.


Install RabbitMQ
----------------
Follow the guides at their website: http://www.rabbitmq.com/download.html.

Refer to the RabbitMQ docs for regular configuration, like logging and
database-file location. The defaults are usable.

Configure RabbitMQ for Devilry
------------------------------
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



Add RabbitMQ settings to Devilry
--------------------------------
Add the following to ``devilry_prod_settings.py`` (change ``secret`` to
match your password)::

    $ BROKER_URL = 'amqp://devilry:secret@localhost:5672/devilryhost'
