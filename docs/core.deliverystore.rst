.. _devilry.apps.core.deliverystore:

================================================================
:mod:`devilry.apps.core.deliverystore` --- DeliveryStore
================================================================

.. currentmodule:: devilry.apps.core.deliverystore



A *DeliveryStore* is a place to put the files from deliveries. In more
technical terms, it is a place where each file related to a
:class:`devilry.apps.core.models.FileMeta` is stored.


Selecting a DeliveryStore
###########################################################

Devilry on comes with one DeliveryStore ready for production use,
:class:`FsDeliveryStore`. To enable a DeliveryStore, you have to set the
``DELIVERY_STORE_BACKEND``-setting in your *settings.py* like this::

    DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsDeliveryStore'

The FsDeliveryStore also require you to define where on the disk you wish to
store your files in the ``DELIVERY_STORE_ROOT``-setting like this::

    DELIVERY_STORE_ROOT = '/path/to/root/directory/of/my/deliverystore'



Creating your own DeliveryStore
###########################################################

To create your own DeliveryStore you have to implement
:class:`DeliveryStoreInterface`. A good example is :class:`FsDeliveryStore`:

    .. literalinclude:: /../devilry/apps/core/deliverystore.py
        :pyobject: FsDeliveryStore


Testing your own DeliveryStore
------------------------------

We provide a mixing-class,
:class:`devilry.apps.core.testhelpers.TestDeliveryStoreMixin`, for you to extend
when writing unit-tests for your DeliveryStore. Here is how we test
:class:`FsDeliveryStore`:

    .. literalinclude:: /../devilry/apps/core/tests.py
        :pyobject: TestFsDeliveryStore

.. currentmodule:: devilry.apps.core.testhelpers

.. autoclass:: devilry.apps.core.testhelpers.TestDeliveryStoreMixin

.. currentmodule:: devilry.apps.core.deliverystore


Setting the DeliveryStore manually - for tests
###########################################################

You might need to set the DeliveryStore manually if you need to handle
deliveries in your own tests. Just set ``devilry.apps.core.FileMeta.deliveryStore``
like this::

    from django.test import TestCase
    from devilry.apps.core.models import FileMeta, Delivery
    from devilry.apps.core.deliverystore import MemoryDeliveryStore

    class MyTest(TestCase):
        def test_something(self):
            FileMeta.deliverystore = MemoryDeliveryStore()
            delivery = Delivery.begin(assignmentgroup, user)
            delivery.add_file('hello.txt', ['hello', 'world'])
            delivery.finish()


API
###########################################################

.. automodule:: devilry.apps.core.deliverystore

