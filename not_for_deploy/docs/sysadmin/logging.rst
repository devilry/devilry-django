####################################
How to configure logging for Devilry
####################################

There are many service levels of a production environment that can be of 
interest to monitor:

- HTTP server (Gunicorn)
- Redis cache
- proxy server (Nginx or Apache)
- file storage

****************
Gunicorn logging
****************

Gunicorn's log level and log file destination are set by its service 
configuration. For a traditional micro-service setup that would mean 
either the Systemd or :doc:`Supervisord <supervisord>` configurations.

Then configure Django's loggers in the ``devilry_settings.py`` file::

    LOGGING = {
        "loggers": {
            "": {
                "level": "INFO",
                "propagate": False,
                "handlers": [
                    "stderr",
                    "mail_admins"
                ]
            },
            "django.db": {
                "level": "WARNING",
                "propagate": False,
                "handlers": [
                    "stderr"
                ]
            },
            "sh": {
                "level": "WARNING",
                "propagate": False,
                "handlers": [
                    "stderr"
                ]
            },
            "devilry_subjectadmin": {
                "level": "INFO",
                "propagate": False,
                "handlers": [
                    "stderr",
                    "mail_admins"
                ]
            },
            "devilry_authenticate": {
                "level": "INFO",
                "propagate": False,
                "handlers": [
                    "stderr"
                ]
            },
            "django.request": {
                "level": "ERROR",
                "propagate": False,
                "handlers": [
                    "stderr",
                    "mail_admins"
                ]
            }
        },
        "disable_existing_loggers": False,
        "handlers": {
            "stderr": {
                "formatter": "verbose",
                "class": "logging.StreamHandler",
                "level": "DEBUG"
            },
            "mail_admins": {
                "include_html": True,
                "class": "django.utils.log.AdminEmailHandler",
                "level": "ERROR"
            }
        },
        "formatters": {
            "verbose": {
                "format": "[%(levelname)s %(asctime)s %(name)s] %(message)s"
            }
        },
        "version": 1,
        "filters": {
            "require_debug_false": {
                "()": "django.utils.log.RequireDebugFalse"
            }
        }
    }

Django's logging is either emailed to the system administrator(s) or handled 
by an error aggregator such as :doc:`Sentry <sentry>`.

********************************************
Configuring Logrotate for Gunicorn and Nginx
********************************************

For a traditional micro-service setup you might also have to add a custom 
configuration for Logrotate.

.. note::

    This assumes the full path to your ``~/devilrydeploy`` directory is
    ``/devilry/devilrydeploy``, that the log files are placed in a 
    ``/logs`` directory inside of it, and that Nginx is used as a proxy
    server  --- adjust accordingly.

Create a Logrotate file (ie. ``/etc/logrotate.d/devilry``) containing the following::

    /devilry/devilrydeploy/logs/nginx*.log {
        create 0644 nginx root
        daily
        rotate 10
        dateext
        missingok
        notifempty
        compress
        delaycompress
        sharedscripts
        postrotate
            # SIGUSR1 will cause nginx to reopen log files
            # Safest way is to use "nginx -s" to send signal
            /usr/sbin/nginx -s reload
        endscript
    }
    
    /devilry/devilrydeploy/logs/gunicorn*.log {
        create 0644 devilrydev devilrydev
        daily
        dateext
        rotate 10
        missingok
        notifempty
        compress
        delaycompress
        sharedscripts
        postrotate
            # Signal USR1 will cause gunicorn to reopen log files
            /bin/pkill --signal USR1 --full /devilry/devilrydeploy/venv/bin/gunicorn
        endscript
    }

