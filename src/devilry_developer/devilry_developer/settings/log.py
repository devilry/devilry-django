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
            'console': {
                'level': 'DEBUG',
                'formatter': 'simple',
                'class': 'logging.StreamHandler'
            },
            'allButExceptionTracebacks': {
                'level': 'ERROR',
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': join(logdir, 'all-but-exceptiontracebacks.devilry.log'),
            },
            'dbfile': {
                'level': 'ERROR',
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': join(logdir, 'db.devilry.log')
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
            },
            'emailfile': {
                'level': 'DEBUG', # Use DEBUG to log all messages, and ERROR to log missing email and SMTP errors
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': join(logdir, 'email.devilry.log')
            }
        },
        'loggers': {
            'devilry.utils.logexceptionsmiddleware': {
                'handlers': ['exceptionTracebacksFile', 'console'],
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
                             'dbdebugfile' # Not useful for production since SQL statement logging is disabled when DEBUG=False.
                            ],
                'level': 'DEBUG',
                'propagate': False
            },
            'devilry.utils.devilry_email': {
                'handlers': ['allButExceptionTracebacks',
                             'emailfile',
                             #'console', # Uncomment this if you want to see every email sent in the console, however it is probably more useful to use emailfile
                            ],
                'level': 'DEBUG',
                'propagate': False
            },
            'devilry': {
                'handlers': ['allButExceptionTracebacks',
                             'console'],
                'level': 'DEBUG',
                'propagate': False
            },
            'devilry_subjectadmin': {
                'handlers': ['allButExceptionTracebacks',
                             'console'],
                'level': 'DEBUG',
                'propagate': False
            },
        }
    }

