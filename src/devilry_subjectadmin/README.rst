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
