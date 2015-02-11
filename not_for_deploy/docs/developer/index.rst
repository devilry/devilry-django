===============================
Devilry developer documentation
===============================


.. note::
    Welcome to the Devilry developer documentation.
    See http://devilry.org/ for general information about Devilry,
    and https://github.com/devilry/devilry-django for the code.


####################################################
Common topics (see Table of contents for all topics)
####################################################


Core
----

.. module:: devilry.apps.core

* **devilry.apps.core.models:** :ref:`API <devilry.apps.core.models>`
* :ref:`userobj`
* :ref:`devilry.apps.core.deliverystore <devilry.apps.core.deliverystore>`


Essential information for new developers
----------------------------------------
* :ref:`devenv`
* :ref:`sourceorganized`
* :ref:`buildout`
* :ref:`testsuite`
* :doc:`devilry.project.develop.teshelpers.corebuilder`
* :doc:`mock`
* :ref:`javascript`
* :doc:`celery`
* More info available on the `Developer wiki page <https://github.com/devilry/devilry-django/wiki/Developer>`_.


How to document Devilry
-----------------------
* `How to write API documentation - wiki page <https://github.com/devilry/devilry-django/wiki/How-to-write-API-documentation>`_
* :ref:`readthedocs` --- If you need to debug build errors from readthedocs.org.


Extending Devilry
-----------------

* :doc:`extend_devilry`
* **Plugins:** :ref:`plugins`, :doc:`Grading system plugins <devilry_gradingsystem>`,
  :doc:`Qualifies for exam <devilry_qualifiesforexam>`.
* **Apps**: Read the `Django docs <https://www.djangoproject.com/>`_.



Apps
----

* :ref:`devilry_subjectadmin`
* :doc:`devilry_qualifiesforexam`
* :doc:`devilry_search`

.. note:: The apps listing is incomplete.


########
Releases
########

* :ref:`releasenoteslisting`


#################
Table of contents
#################

.. toctree::
    :maxdepth: 2

    core.models
    userobj
    core.deliverystore

    devenv
    sourceorganized
    buildout
    testsuite
    mock
    devilry.project.develop.teshelpers.corebuilder
    testhelper
    extend_devilry
    create_app
    plugins
    celery

    devilry_subjectadmin
    devilry_qualifiesforexam
    devilry_gradingsystem
    devilry_search
    devilry_theme

    devilry.utils

    readthedocs
    i18n
    javascript
    pycharm

    releasenoteslisting
    release
