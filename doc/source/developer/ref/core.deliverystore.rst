.. _ref-devilry.core.deliverystore:

================================================================
:mod:`devilry.core.deliverystore` --- DeliveryStore
================================================================

.. currentmodule:: devilry.core.deliverystore



A *DeliveryStore* is a place to put the files from deliveries. In more
technical terms, it is a place where each file related to a
ref:`devilry.core.models.FileMeta` is stored.


Selecting a DeliveryStore
###########################################################

Devilry on comes with one DeliveryStore ready for production use,
:class:`FsDeliveryStore`. To enable a DeliveryStore, you have to set the
``DELIVERY_STORE_BACKEND``-setting in your *settings.py* like this::

    DELIVERY_STORE_BACKEND = 'devilry.core.deliverystore.FsDeliveryStore'

The FsDeliveryStore also require you to define where on the disk you wish to
store your files in the ``DELIVERY_STORE_ROOT``-setting like this::

    DELIVERY_STORE_ROOT = '/path/to/root/directory/of/my/deliverystore'



Creating your own DeliveryStore
###########################################################

To create your own DeliveryStore you have to implement
:class:`DeliveryStoreInterface`. A good example is :class:`FsDeliveryStore`:

    .. literalinclude:: /../../devilry/core/deliverystore.py
        :pyobject: FsDeliveryStore


Testing your own DeliveryStore
------------------------------

We provide a mixing-class,
:class:`devilry.core.testhelpers.TestDeliveryStoreMixin`, for you to extend
when writing unit-tests for your DeliveryStore. Here is how we test
:class:`FsDeliveryStore`:

    .. literalinclude:: /../../devilry/core/tests.py
        :pyobject: TestFsDeliveryStore

.. currentmodule:: devilry.core.testhelpers

.. autoclass:: devilry.core.testhelpers.TestDeliveryStoreMixin

.. currentmodule:: devilry.core.deliverystore

API
###########################################################

.. automodule:: devilry.core.deliverystore

