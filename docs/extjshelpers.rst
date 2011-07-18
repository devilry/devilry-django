.. _extjshelpers:

===============================================================
:mod:`devilry.apps.extjshelpers` --- ExtJS helpers
===============================================================

**TODO:** Tutorial and more docs.




Template filters
================

To use these filters, add the following to your Django template::

    {% load extjs %}

Note that the examples below assume that ``devilry.examiner.restful.RestfulSimplifiedDelivery``
is available as a template variable as ``RestfulSimplifiedDelivery``. You may use any
:ref:`RESTful class <restful>` in place of ``RestfulSimplifiedDelivery``.


extjs_model
-----------

.. code-block:: javascript

    // Create a variable with the extjsmodel class definition
    var deliverymodel = {{ RestfulSimplifiedDelivery|extjs_model }};

    // Often you will rather define a model and use it later with the
    // extjs_modelname filter (or a combination of both approaches)
    {{ RestfulSimplifiedDelivery|extjs_model }};
    var deliverymodelname = {{ RestfulSimplifiedDelivery|extjs_modelname }};
    var delivery = Ext.create(deliverymodelname, {
        // Data needed to create a delivery ...
    });
    

.. autofunction:: devilry.apps.extjshelpers.templatetags.extjs.extjs_model


extjs_modelname
-----------------

.. code-block:: javascript

    var modelname = {{ RestfulSimplifiedDelivery|extjs_modelname }};

.. autofunction:: devilry.apps.extjshelpers.templatetags.extjs.extjs_modelname


extjs_combobox_model
--------------------

.. code-block:: javascript

    var comboboxmodel = {{ RestfulSimplifiedDelivery|extjs_combobox_model }};

.. autofunction:: devilry.apps.extjshelpers.templatetags.extjs.extjs_combobox_model

extjs_store
-----------

.. code-block:: javascript

    var deliverystore = {{ RestfulSimplifiedDelivery|extjs_store }};

.. autofunction:: devilry.apps.extjshelpers.templatetags.extjs.extjs_store


extjs_form_items
----------------

.. code-block:: javascript

    var formitems = {{ RestfulSimplifiedDelivery|extjs_form_items }};

.. autofunction:: devilry.apps.extjshelpers.templatetags.extjs.extjs_form_items


extjs_foreignkeys
-----------------

.. code-block:: javascript

    var foreignkeys = {{ RestfulSimplifiedDelivery|extjs_foreignkeys }};

.. autofunction:: devilry.apps.extjshelpers.templatetags.extjs.extjs_foreignkeys


Low-level API for filters
===========================

.. automodule:: devilry.apps.extjshelpers.modelintegration
.. automodule:: devilry.apps.extjshelpers.storeintegration
.. automodule:: devilry.apps.extjshelpers.formintegration


Extensions to the RESTful API
=============================

See :ref:`restful`.

.. automodule:: devilry.apps.extjshelpers
