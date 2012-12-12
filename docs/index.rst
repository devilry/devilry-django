======================================================================
Devilry developer documentation overview
======================================================================


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
* :ref:`testsuite`
* :ref:`testhelper`
* :ref:`javascript`


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

.. note:: The apps listing is incomplete.


#######################################################################
Table of contents
#######################################################################
.. toctree::

    core.models
    userobj
    core.deliverystore

    testsuite
    testhelper
    plugins

    devilry_subjectadmin

    apps.gradeeditors
    utils.assignmentgroup
    utils.ordereddict
    utils.delivery_collection
    utils.groupnodes
    utils.devilry_email

    readthedocs
    i18n
    javascript
    pycharm



#######################################################################
Indices and tables
#######################################################################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

