======================================================================
Devilry developer documentation overview
======================================================================


.. warning::
    This documentation is for the upcoming Devilry 1.2.1 release.
    The docs for the current stable version is
    `here <http://devilry.org/devilry-django/dev/>`_.


.. note::
    Welcome to the Devilry developer documentation.
    See http://devilry.org/ for general information about Devilry,
    and https://github.com/devilry/devilry-django for the code.


#######################################################################
Common topics (see Table of contents for all topics)
#######################################################################


Core
----------------------------------------------------------------------

* **devilry.apps.core.models:** :ref:`API <devilry.apps.core.models>`
* :ref:`userobj`
* :ref:`devilry.apps.core.deliverystore <devilry.apps.core.deliverystore>`


Essential information for new developers
----------------------------------------
* :ref:`devenv`
* :ref:`sourceorganized`
* :ref:`buildout`
* :ref:`testsuite`
* :ref:`testhelper`
* :ref:`javascript`
* More info available on the `Developer wiki page <https://github.com/devilry/devilry-django/wiki/Developer>`_.


How to document Devilry
---------------------------------------------------------------------
* `How to write API documentation - wiki page <https://github.com/devilry/devilry-django/wiki/How-to-write-API-documentation>`_
* :ref:`readthedocs` --- If you need to debug build errors from readthedocs.org.


Plugin development
----------------------------------------------------------------------

* **The basics:** :ref:`plugins`
* **Grade editors:** :ref:`Overview <apps.gradeeditors>`


RESTful API
----------------------------------------------------------------------

* **Old rest APIs**: See the old docs: http://devilry.org/devilry-django/dev/
* **New rest APIs**: Uses Djangorestframework, which generates docs that can be browsed. We are missing a
  listing of the URLs of all our new APIs, so please contact us via Github if you need help finding them.


Apps
----------------------------------------------------------------------

* :ref:`devilry_subjectadmin`
* :ref:`devilry_qualifiesforexam`

.. note:: The apps listing is incomplete.


#######################################################################
Releases
#######################################################################

* :ref:`releasenoteslisting`


#######################################################################
Table of contents
#######################################################################
.. toctree::

    core.models
    userobj
    core.deliverystore

    devenv
    sourceorganized
    buildout
    testsuite
    testhelper
    plugins

    devilry_subjectadmin
    devilry_qualifiesforexam

    apps.gradeeditors
    utils.assignmentgroup
    utils.ordereddict
    utils.delivery_collection
    utils.groupnodes
    utils.devilry_email
    utils.groups_groupedby_relatedstudent_and_assignment

    readthedocs
    i18n
    javascript
    pycharm

    releasenoteslisting



#######################################################################
Indices and tables
#######################################################################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

