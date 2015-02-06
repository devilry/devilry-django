from os.path import join

def create_logging_conf(logdir):
    return {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': '[%(levelname)s %(asctime)s %(name)s] %(message)s'
            },
            'simple': {
                'format': '[%(levelname)s] %(message)s'
            },
        },

        'handlers': {
            # 'sentry': {
            #     'level': 'DEBUG',
            #     'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            # },
            'console': {
                'level': 'DEBUG',
                'formatter': 'verbose',
                'class': 'logging.StreamHandler'
            },
            'allButExceptionTracebacks': {
                'level': 'DEBUG',
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': join(logdir, 'all-but-exceptiontracebacks.devilry.log'),
            },
            'dbfile': {
                'level': 'ERROR',
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': join(logdir, 'dberrors.devilry.log')
            },
            'dbdebugfile': { # Shows the SQL statements
                'level': 'DEBUG',
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': join(logdir, 'debug-containing-sqlstatements.db.devilry.log')
            },
            'requestfile': {
                'level': 'ERROR',
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': join(logdir, 'request.devilry.log')
            },
            'exceptionTracebacksFile': {
                'level': 'ERROR',
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': join(logdir, 'exception.devilry.log')
            }
        },
        'loggers': {
            'devilry.utils.logexceptionsmiddleware': {
                'handlers': ['exceptionTracebacksFile', 'console'],#, 'sentry'],
                'level': 'ERROR',
                'propagate': False
            },
            'django.request': {
                'handlers': ['allButExceptionTracebacks',
                             'requestfile'],
                'level': 'ERROR',
                'propagate': False
            },
            'django.db.backends': {
                'handlers': ['allButExceptionTracebacks',
                             'dbfile',
                             #'console', # Comment in to see SQL statements in the log
                             'dbdebugfile' # Not useful for production since SQL statement logging is disabled when DEBUG=False.
                            ],
                'level': 'DEBUG',
                'propagate': False
            },
            'devilry.utils.devilry_email': {
                'handlers': ['allButExceptionTracebacks',
                             'emailfile',
                             #'sentry',
                             #'console', # Uncomment this if you want to see every email sent in the console, however it is probably more useful to use emailfile
                            ],
                'level': 'DEBUG',
                'propagate': False
            },
            'selenium.webdriver.remote.remote_connection': {
                'handlers': ['allButExceptionTracebacks', 'console'],
                'level': 'INFO',
                'propagate': False
            },
            'devilry.devilry_search.tasks': {
                'handlers': ['allButExceptionTracebacks'],
                'level': 'INFO',
                'propagate': False
            },
            '': {
                'handlers': ['allButExceptionTracebacks',
                             #'sentry',
                             'console'],
                'level': 'DEBUG',
                'propagate': False
            },
        }
    }

