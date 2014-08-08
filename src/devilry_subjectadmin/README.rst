###########################
devilry_subjectadmin
###########################

Subject (course) administrator interface for Devilry.


Install
=======

Add ``devilry_subjectadmin`` to ``INSTALLED_APPS``, and add::

    (r'^devilry_usersearch/', include('devilry_usersearch.urls'))

to ``urlpatterns`` in ``urls.py``. You must also install the dependencies:

    - ``devilry_theme``
    - ``devilry_extjsextras``
    - ``devilry_usersearch``

See their docs for more info.


Logging
=======

All changes are logged to the ``devilry_subjectadmin`` logger. Normal changes
are logged as ``INFO``. If you want to keep these logs, add something like this
to your ``LOGGING['loggers']`` in ``settings.py``::

    'devilry_subjectadmin': {
        'handlers': ['myHandler'],
        'level': 'INFO',
        'propagate': False
    }
