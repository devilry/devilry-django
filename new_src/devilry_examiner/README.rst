###########################
devilry_examiner
###########################

Examiner interface for devilry


Install
=======

Add ``devilry_examiner`` to ``INSTALLED_APPS``, and add::

    - ``devilry_theme``
    - ``devilry_extjsextras``

See their docs for more info.


Logging
=======

All changes are logged to the ``devilry_examiner`` logger. Normal changes
are logged as ``INFO``. If you want to keep these logs, add something like this
to your ``LOGGING['loggers']`` in ``settings.py``::

    'devilry_examiner': {
        'handlers': ['myHandler'],
        'level': 'INFO',
        'propagate': False
    }
