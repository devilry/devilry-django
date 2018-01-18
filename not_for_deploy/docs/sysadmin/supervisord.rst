#######################################################################
Setup Supervisord for process management, log handling and log rotation
#######################################################################

.. note::

    This assumes the full path to your ``~/devilrydeploy``-directory is
    ``/home/devilryrunner/devilrydeploy`` --- adjust accordingly.


Create a Supervisord configuration file
=======================================

Create a file named ``~/devilrydeploy/supervisord.conf`` and add the following::

    [supervisord]
    childlogdir = /home/devilryrunner/devilrydeploy/log
    logfile = /home/devilryrunner/devilrydeploy/log/supervisord.log
    logfile_maxbytes = 50MB
    logfile_backups = 30
    loglevel = info
    pidfile = /home/devilryrunner/devilrydeploy/var/supervisord.pid
    umask = 022
    nodaemon = false
    nocleanup = false

    [inet_http_server]
    port = 9001
    username = devilryadmin
    password = secret

    [supervisorctl]
    serverurl = http://localhost:9001
    username = devilryadmin
    password = secret

    [rpcinterface:supervisor]
    supervisor.rpcinterface_factory=supervisor.rpcinterface:make_main_rpcinterface

    [program:gunicorn]
    command = /home/devilryrunner/devilrydeploy/venv/bin/gunicorn devilry.project.production.wsgi -b 127.0.0.1:8002 -w 12 --timeout 300
    environment = DJANGO_SETTINGS_MODULE=devilry_settings
    process_name = gunicorn
    directory = /home/devilryrunner/devilrydeploy
    redirect_stderr = true
    stdout_logfile = /home/devilryrunner/devilrydeploy/log/gunicorn.log
    stdout_logfile_maxbytes = 150MB
    stdout_logfile_backups = 15

    [program:rqworker]
    command = /home/devilryrunner/devilrydeploy/venv/bin/python manage.py rqworker default email highpriority
    process_name = rqworker
    directory = /home/devilryrunner/devilrydeploy
    redirect_stderr = true
    stdout_logfile = /home/devilryrunner/devilrydeploy/log/rq.log
    stdout_logfile_maxbytes = 150MB
    stdout_logfile_backups = 15



Password and security
=====================
Make sure you set some other password than ``secret`` in
the ``[inet_http_server]`` and ``[supervisorctl]`` sections,
and make sure ``~/devilrydeploy/supervisord.conf`` is only
accessible to the ``devilryrunner``-user.


Create the var/ and log/ directories
====================================
The supervisord.conf file refers to the ``~/devilrydeploy/var/`` and ``~/devilrydeploy/log/``
directories. These must be created::

    $ cd ~/devilrydeploy
    $ mkdir var/ log/


Make sure all services work as excpected
========================================
To run supervisord in the foreground (for testing), run::

    $ cd ~/devilrydeploy
    $ venv/bin/supervisord -n -c supervisord.conf

You should now be able to open http://localhost:8002 in a browser and use Devilry.
Use ``ctrl-c`` to kill supervisord and all the services it is running.


.. _run-supervisord-for-production:

Run Supervisord for production
==============================

To run supervisord in the background with a PID, run::

    $ cd ~/devilrydeploy
    $ venv/bin/supervisord -c supervisord.conf


.. warning::

    Do NOT run supervisord as root. Run it as the ``devilryrunner`` user.


.. _supervisord-initscript:

Init script
===========
The following init script works well. You need to adjust the ``DAEMON``-variable:

.. literalinclude:: _static/supervisord
    :language: bash
