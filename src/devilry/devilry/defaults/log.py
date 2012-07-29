"""
Sane default logging setup.
"""

from os.path import join


def create_logging_config(mail_admins=True,
                          mail_admins_level='ERROR',
                          log_to_file=False,
                          log_to_file_dir=None,
                          log_to_stderr=True,
                          dangerous_actions_loglevel='INFO',
                          django_loglevel='ERROR',
                          request_loglevel='ERROR',
                          devilry_loglevel='ERROR'):
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

    :param log_to_file:
        Log to file?
    :param log_to_file_dir:
        The directory to put files in if ``log_to_file==True``.
    :param log_to_stderr:
        Log to stderr?
    :param log_dangerous_actions:
        Log dangerous actions? Set to ``"INFO"`` to log any somewhat dangerous
        actions (I.E.: creating a deadline, update a subject, ...). Set to
        ``"WARN"`` to log only really dangerous actions, like deleting something.
        When ``log_to_file==True``, we log dangerous actions actions to
        ``<log_to_file_dir>/dangerous_actions.log``.
    :param django_loglevel:
        Loglevel for logs from the django namespace. See ``mail_admins_level`` for valid levels.
    :param request_loglevel:
        Loglevel for request logs (from the django.request namespace). See ``mail_admins_level`` for valid levels.
    :param devilry_loglevel:
        Loglevel for log messages from Devilry (from the devilry namespace). See ``mail_admins_level`` for valid levels.

    :raise ValueError:
        If ``log_to_file_dir`` is not given when ``log_to_file==True``.
    """

    if log_to_file and not log_to_file_dir:
        raise ValueError('create_logging_config(...) requires a ``log_to_file_dir`` if ``log_to_file==True``.')


    default_handlers = []
    if mail_admins:
        default_handlers.append('mail_admins')
    if log_to_stderr:
        default_handlers.append('stderr')

    # Handlers used for everything but requests and dangerous actions
    handlers = default_handlers[:] #copy
    if log_to_file:
        handlers.append('logfile')

    # We use a custom set of handlers for request logging
    request_handlers = default_handlers[:] #copy
    if log_to_file:
        request_handlers.append('requestfile')

    # We use a custom set of handlers for dangerous actions
    request_handlers = default_handlers[:] #copy
    if log_to_file:
        request_handlers.append('dangerousfile')

    return {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': '[%(levelname)s %(asctime)s %(name)s] %(message)s'
            }
        },

        'handlers': {
                     # We set all handlers except mail_admins to level=DEBUG, and configure the actual loglevel in the loggers
            'stderr': {
                'level': 'DEBUG',
                'formatter': 'simple',
                'class': 'logging.StreamHandler'
            },
            'logfile': {
                'level': 'DEBUG',
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': join(log_to_file_dir, 'devilry.log'),
            },
            'dangerousfile': {
                'level': 'DEBUG',
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': join(log_to_file_dir, 'dangerous_actions.log'),
            },
            'requestfile': {
                'level': 'DEBUG',
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': join(log_to_file_dir, 'requests.log')
            },
            'mail_admins': {
                'level': mail_admins_level,
                'class': 'django.utils.log.AdminEmailHandler',
                'include_html': True # The traceback email includes an HTML attachment containing the full content of the debug Web page that would have been produced if DEBUG were True. 
            }
        },
        'loggers': {
            'django.request': {
                'handlers': request_handlers,
                'level': request_loglevel,
                'propagate': False
            },
            'django': {
                'handlers': handlers,
                'level': django_loglevel,
                'propagate': False
            },
            'devilry': {
                'handlers': request_handlers,
                'level': request_handlers,
                'propagate': False
            },
            'devilry_subjectadmin': {
                'handlers': request_handlers,
                'level': dangerous_actions_loglevel,
                'propagate': False
            }
        }
    }

