"""
Sane default logging setup.
"""


def create_logging_config(
        mail_admins=True,
        mail_admins_level='ERROR',
        dangerous_actions_loglevel='INFO',
        django_loglevel='INFO',
        db_loglevel='WARNING',
        sh_loglevel='WARNING',
        request_loglevel='ERROR'):
    """
    Returns a logging config that can be used for ``settings.LOGGING``.

    :param mail_admins:
        Send error logs to the admins defined in ``settings.ADMINS``? The level
        of errors to send to admins is configured by ``mail_admins_level``.
    :param mail_admins_level:
        See ``mail_admins``. Valid levels are:

            - DEBUG
            - INFO
            - WARN
            - ERROR

    :param dangerous_actions_loglevel:
        Log dangerous actions? Set to ``"INFO"`` to log any somewhat dangerous
        actions (I.E.: creating a deadline, update a subject, ...). Set to
        ``"WARNING"`` to log only really dangerous actions, like deleting something.
        When ``log_to_file==True``, we log dangerous actions actions to
        ``<log_to_file_dir>/dangerous_actions.log``.
    :param sh_loglevel:
        Loglevel for the `sh` library used to run some shell commands.
        Defaults to "WARNING".
    :param db_loglevel:
        Loglevel for Django database actions.
        Defaults to "WARNING". If you set this to "DEBUG", ALL
        SQL queries are logged. That is performance intensive,
        and should only be used for debugging!
    :param django_loglevel:
        Loglevel for logs from the django namespace. See ``mail_admins_level`` for valid levels.
    :param request_loglevel:
        Loglevel for request logs (from the django.request namespace). See ``mail_admins_level`` for valid levels.

    :raise ValueError:
        If ``log_to_file_dir`` is not given when ``log_to_file==True``.
    """

    handlers = ['stderr']
    if mail_admins:
        handlers.append('mail_admins')

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[%(levelname)s %(asctime)s %(name)s] %(message)s'
            }
        },

        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },

        'handlers': {
            # We set all handlers except mail_admins to level=DEBUG, and configure the actual loglevel in the loggers
            'stderr': {
                'level': 'DEBUG',
                'formatter': 'verbose',
                'class': 'logging.StreamHandler'
            },
            'mail_admins': {
                'level': mail_admins_level,
                'class': 'django.utils.log.AdminEmailHandler',
                # The traceback email includes an HTML attachment containing the
                # full content of the debug Web page that would have been produced
                # if DEBUG were True.
                'include_html': True
            }
        },
        'loggers': {
            'django.request': {
                'handlers': handlers,
                'level': request_loglevel,
                'propagate': False
            },
            'devilry_subjectadmin': {
                'handlers': handlers,
                'level': dangerous_actions_loglevel,
                'propagate': False
            },
            'django.db': {
                'handlers': ['stderr'],
                'level': db_loglevel,
                'propagate': False
            },
            'sh': {
                'handlers': ['stderr'],
                'level': sh_loglevel,
                'propagate': False
            },
            'MARKDOWN': {
                'handlers': ['stderr'],
                'level': 'INFO',
                'propagate': False
            },
            'chardet.charsetprober': {
                'handlers': ['stderr'],
                'level': 'INFO',
                'propagate': False
            },
            '': {
                'handlers': handlers,
                'level': django_loglevel,
                'propagate': False
            },

        }
    }

