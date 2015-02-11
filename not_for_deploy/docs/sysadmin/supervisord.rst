.. _supervisord-configure:

=============================================
Configure supervisord (logging, pidfile, ...)
=============================================
We handle all logging through Supervisord, so you will probably at least want
to configure where we log to.

Supervisor variables are now iniatially defined in the ``variables``
section in ``buildout-base.cfg`` and can be overridden by adding a ``variables``
section in your own buildout config file. Logging directory and rotation parameters
should be redefined accordingly::


    [variables]
    # The full path to the supervisord log directory.
    # Defaults to /path/to/devilrybuild/var/log/
    # Note: This setting is added by our buildout-base.cfg, and not by the
    # supervisor buildout recipe.
    #logdir = 

    # Where logs are placed on the filesystem
    
    logdir = ${buildout:directory}/var/log
    
    # Max number of bytes in a single log
    
    logfile-maxbytes = 50MB
    
    # Number of times a log rotates - note that each program running under
    # supervisor has 2 logs (stdout and stderr), and each log will consume
    # ``logfile-maxbytes * logfile-backups`` of disk space.
    
    logfile-backups = 30

For more information on how ``supervisord`` deals with rotation see: http://supervisord.org/logging.html#activity-log-rotation

=========================================
Details. What is being logged and where?
=========================================

The different modules that are configured is running as a subprocess within ```supervisord``
and will be captured by ``supervisord``. To mantain full control of the logging environment
it is important to configure each submodule in order to avoid ``supervisord`` *AUTO* log mode
in which every log is stored on temporary terms. Every configuration parameter will be included in
the final ``supervisord.conf`` file in is ``[program:x]`` block. We never edit the configure directly
but tunes the parameters from within the buildout files. So in ``buildout-base.cfg`` each process are configured
with the extracted variables from the ``[variables]`` section you defined above. Check out the file
`buildout-base.cfg <https://github.com/devilry/devilry-deploy/blob/master/buildout/buildout-base.cfg>`_ and look for 
``${variables:x}`` where x is the name of the variable you have redefined. 

As an example we look into gunicorn configuration::

    [gunicorn]
    workers = 8
    executable = ${variables:django_managepy}
    address = 127.0.0.1
    port = 8002
    args = run_gunicorn -b ${gunicorn:address}:${gunicorn:port} -w ${gunicorn:workers} --timeout 180
    cwd = ${buildout:directory}
    logfile-maxbytes = ${variables:logfile-maxbytes}
    logfile-backups = ${variables:logfile-backups}
    logoptions = stdout_logfile=${variables:logdir}/gunicorn.stdout.log stdout_logfile_maxbytes=${gunicorn:logfile-maxbytes} stdout_logfile_backups=${gunicorn:logfile-backups} stderr_logfile=${variables:logdir}/gunicorn.stderr.log stderr_logfile_maxbytes=${gunicorn:logfile-maxbytes} stderr_logfile_backups=${gunicorn:logfile-backups}

``executable = ${variables:django_managepy}`` 
    This is often not redefined. Gunicorn is started by using the ``run_gunicorn`` command to the
    django managment script to ensure that gunicorn is running with correct django setup.
    
``logfile-maxbytes = ${variables:logfile-maxbytes}``
    Defined as the maximum number of bytes logged
    
``logfile-backups = ${variables:logfile-backups}```
    Defined as the number of rotations for each logged reaching ``logfile-maxbytes`` stored data
    
``logoptions = stdout_logfile=${variables:logdir}/gunicorn.stdout.log``
    This is the options to the gunicorn application and directly affects the gunicorn logging behaviour within supervisord.
    every application setup for logging will have the same logfile naming convention where the ``logdir`` is
    defined and then the name will consist of ``<appname>.<stream>.log`` Both error and standard out streams are configured.
    
Gunicorn
---------
Serves the the Devilry site to the outgoing server. Gunicorn is a WSGI server to be used behind a HTTP proxy server
for incoming request-managment.

What is logged ?
^^^^^^^^^^^^^^^^

Celery Worker
--------------
Manage the Celery Workers configured for task managment.

What is logged ?
^^^^^^^^^^^^^^^^

Celery Beat
------------
Celery Beat is the scheduler that starts the given tasks at defined intervals

What is logged ?
^^^^^^^^^^^^^^^^

Run_Solr
---------
This is a buildout recipe for creating a ``run_solr.sh`` file. A script that ease the Apache Solr configuration
for use with HayStack. It is the search engine of Devilry.

What is logged ?
^^^^^^^^^^^^^^^^

Rebuild the Supervisord config (output in ``parts/supervisor/supervisord.conf``)::

    $ bin/buildout

And restart supervisord.

See the `Buildout recipe <http://pypi.python.org/pypi/collective.recipe.supervisor/>`_
and the `Supervisord docs <http://supervisord.org/>`_ for more details.


.. _supervisord-initscript:

Init script
===========
The following init script works well. You need to adjust the ``DAEMON``-variable (`download <_static/supervisord>`_):

.. literalinclude:: /_static/supervisord
    :language: bash


Harden supervisord
==================

The default configuration if for a dedicated server. Supervisorctl uses a
password with the local Supervisord server, which needs to be a better password
in a shared environment. This should not be a problem since it is madness to 
host Devilry on a shared host in any case, but if you need to harden Supervisord,
refer to the docs linked above.
