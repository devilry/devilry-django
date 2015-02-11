.. _deploy:

**************
Build Devilry
**************
Devilry does not come pre-packaged. Instead, we deploy using `buildout <http://www.buildout.org/>`_.
There is several reasons for that:

- It is easier to maintain deployment through buildout.
- It is easier to customize Devilry when we do not have to force defaults on
  people. With the current method of deployment, admins can easily intergrate
  local devilry addons.
- The method we are using seems to work very well for the Plone CMS.

What this means for you is that you have to setup a very minimal
buildout-config instead of downloading an archive and unzipping it.


Create a system user for Devilry
===================================
You should run Devilry as a non-privledged user. We suggest you name the user
something like ``devilryrunner``. Run all commands in this documentation as
this user unless stated otherwise. 


.. _configure_buildout:

Configure buildout
==================
Create a directory that will be used to configure your Devilry build::

    $ mkdir devilrybuild

Create a configuration file named ``buildout.cfg`` in the directory. Add the
following to the configuration file::

    [buildout]
    extends = https://raw.github.com/devilry/devilry-deploy/REVISION/buildout/buildout-base.cfg

Replace ``REVISION`` (in the extends url) with the Devilry version you want to
use (E.g.: ``v1.2.1``). See `the tag listing on github
<https://github.com/devilry/devilry-deploy/tags>`_ for a list of all releases,
and refer to :devilrydoc:`The releasenotes listing <releasenoteslisting.html>`
for the information about each release.


Install required system packages
================================
See :ref:`required-system-packages`.


Initialize the buildout
=======================

CD to the directory and run the following commands to download Devilry and
all dependencies into a Python virtualenv. The end result is a
selfcontained devilry build that only depends on the availability of a 
compatible Python interpreter to run. The virtualenv is not affected by
other Python packages installed globally::

    $ cd devilrybuild/
    $ mkdir -p buildoutcache/dlcache
    $ virtualenv --no-site-packages .
    $ bin/easy_install zc.buildout
    $ bin/buildout "buildout:parts=download-devilryrepo" && bin/buildout


Configure Devilry
=================
To configure Devilry, you need to create a Python module containing a
config-file named ``devilry_prod_settings.py``. First create a directory for
your Devilry configurations::

    $ mkdir /etc/devilry

turn the directory into a Python module::

    $ touch /etc/devilry/__init__.py

and add your own ``devilry_prod_settings.py`` to the directory. This is a good starting point:

.. literalinclude:: /examples/devilry_prod_settings.py
    :language: python

The config-file can contain any official Django settings, and Devilry provides
some extra settings that should be useful:

- :ref:`Django email backends <django:topic-email-backends>`
- :djangodoc:`Django settings <topics/settings/>`
- `Devilry settings <https://github.com/devilry/devilry-django/blob/1728d4e01abd7aed58da86be9fccd09cfcaadc08/src/devilry_settings/devilry_settings/default_settings.py>`_ (scroll down to the *Default for settings defined by Devilry* section).
- `django-celery-email <https://pypi.python.org/pypi/django-celery-email>`_ is
  an addon that sends email in a background queue. The addon is installed by
  devilry-deploy by default, and is highly recommended (see
  https://github.com/devilry/devilry-django/issues/477).


.. note::

    You can put ``devilry_prod_settings.py`` in another directory. You just have to add::

        [devilry]
        configdir = /etc/devilry

    to your ``buildout.cfg`` and re-run ``bin/buildout``.
        


Create the database
===================
When you have configured a database in ``devilry_prod_settings.py``, you
can use the following command to create your database::

    $ cd /path/to/devilrybuild
    $ bin/django.py syncdb

The script will ask you to create a superuser. Choose a strong password - this
user will have complete access to everything in Devilry.


Install RabbitMQ
=================
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
-------------------------------
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
---------------------------------
Add the following to ``devilry_prod_settings.py`` (change ``secret`` to
match your password)::

    $ BROKER_URL = 'amqp://devilry:secret@localhost:5672/devilryhost'


Test the install
================
See :ref:`debug-devilry-problems`.



Setup Devilry for production
============================
Collect all static files in the ``static/``-subdirectory::

    $ bin/django.py collectstatic


Make sure all services work as excpected
----------------------------------------
All Devilry services is controlled to Supervisord. This does not include your
database or webserver.

To run supervisord in the foreground for testing/debugging, enable DEBUG-mode
(see :ref:`debug-devilry-problems`), and  run::

    $ bin/supervisord -n

Make sure you disable DEBUG-mode afterwards.


.. _run-supervisord-for-production:

Run Supervisord for production
-------------------------------

To run supervisord in the background with a PID, run::

    $ bin/supervisord

See :ref:`supervisord-configure` to see and configure where the PID-file is
written, and for an init-script example.

.. warning::
    Do NOT run supervisord as root. Run it as an unpriviledged used, preferably
    a user that is only used for Devilry. Use the ``supervisord-user``, as shown
    in :ref:`supervisord-configure`, to define a user if running supervisord as
    root.


Configure your webserver
------------------------
You need to configure your webserver to act as a reverse proxy for all URLS
except for the ``/static/``-url. The proxy should forward requests to the
Devilry WSGI server (gunicorn). Gunicorn runs  on ``127.0.0.0:8002``.

The webserver should use SSL.

.. seealso:: :ref:`nginx`.


Whats next?
===========

- :ref:`update`
- :ref:`supervisord-initscript`
