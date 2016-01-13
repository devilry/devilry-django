.. _devilry.apps.core.deliverystore:

========================================================
:mod:`devilry.apps.core.deliverystore` --- DeliveryStore
========================================================


.. deprecated:: 3.0
   This module is deprecated in 3.0 and will be removed
   in a future release.

.. currentmodule:: devilry.apps.core.deliverystore



A *DeliveryStore* is a place to put the files from deliveries. In more
technical terms, it is a place where each file related to a
:class:`devilry.apps.core.models.FileMeta` is stored.


Selecting a DeliveryStore
#########################

Devilry on comes with one DeliveryStore ready for production use,
:class:`FsDeliveryStore`. To enable a DeliveryStore, you have to set the
``DELIVERY_STORE_BACKEND``-setting in your *settings.py* like this::

    DELIVERY_STORE_BACKEND = 'devilry.apps.core.deliverystore.FsDeliveryStore'

The FsDeliveryStore also require you to define where on the disk you wish to
store your files in the ``DELIVERY_STORE_ROOT``-setting like this::

    DELIVERY_STORE_ROOT = '/path/to/root/directory/of/my/deliverystore'



Creating your own DeliveryStore
###############################

To create your own DeliveryStore you have to implement
:class:`DeliveryStoreInterface`. A good example is :class:`FsDeliveryStore`:

    .. literalinclude:: /../../devilry/apps/core/deliverystore.py
        :pyobject: FsDeliveryStore


.. currentmodule:: devilry.apps.core.testhelpers

.. autoclass:: devilry.apps.core.testhelpers.DeliveryStoreTestMixin

.. currentmodule:: devilry.apps.core.deliverystore


Setting the DeliveryStore manually - for tests
##############################################

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



The recommended production deliverystore
########################################

If you store files in a traditional file system:
    The recommended DeliveryStore for traditional filesystems
    is :class:`devilry.apps.core.deliverystore.FsHierDeliveryStore`.

    It stores files in a filesystem hierarcy with one directory for each
    Delivery, with the delivery-id as name. In each delivery-directory, the
    files are stored by FileMeta id.

If you store files in a modern cloud file system like Amazon S3:
    The recommended DeliveryStore for cloud file systems that have no
    upper limit on the number of files in a single directory is
    :class:`devilry.apps.core.deliverystore.DjangoStorageDeliveryStore`.


Directory hierachy
==================

The delivery directories are stored in a
hierarchy with two parent directories. The parent directories are numeric intervals.
We have one top-level directory for each N in ``interval_size*interval_size*N``. Within each
toplevel directory, we have one subdirectory for each N in
``interval_size*N``.


Directory hierarchy example
===========================

For ``interval_size`` of ``1000``, this will use the following hierarchy::


    0/
        0/
            0/
            1/
            .
            .
        1/
            1000/
            2000/
            .
            .
        2/
        .
        .
        999/
    1/
        0/
            1000000/
            1000001/
            .
            .
        1/
            1001000/
            1001001/
        2/
        .
        .
        999/
    2/
    .
    .
    999/


API
###

.. automodule:: devilry.apps.core.deliverystore
    :members:
