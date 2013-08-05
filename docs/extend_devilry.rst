###############################################
Extend Devilry --- intro/overview
###############################################


*******************
Types of extensions
*******************
    
Apps
====
Apps are simply normal Django_ apps that may or may not use our `public python
APIs <public_python_apis>`_.


Plugin
======
A plugin is a regular Django_ app app that 




.. _public_python_apis:

******************
Public python APIs
******************

At this time, the current APIs are public:

- :mod:`devilry.apps.core`
- :mod:`devilry.utils`
- :mod:`devilry_theme`
- :mod:`devilry_qualifiesforexam`



***************************
Public HTML/JavaScript APIs
***************************

:mod:`devilry_header`
=====================
Defines the Devilry header (the black bar at the top of the page), as both an
ExtJS widget, and as a standalone widget that can be used in plain HTML pages,
or with other javascript libraries.

Take a look at the source code for ``devilry_student`` for a relatively simple
app that uses Devilry header. We set up the header in
``static/devilry_student/app.js``.





.. _Django: https://www.djangoproject.com/
