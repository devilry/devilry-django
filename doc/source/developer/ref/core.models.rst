.. _ref-devilry.core.models:

=========================================================
:mod:`devilry.core.models` --- Devilry core datastructure
=========================================================

.. For some reason required to make cross references work.
   http://groups.google.com/group/sphinx-dev/browse_thread/thread/dd921549bc146a5c/2f39d79ce46d447f
.. currentmodule:: devilry.core.models


Check out the :ref:`overview` if you need a simple overview of the different
components.


BaseNode
===========================================================

.. autoclass:: devilry.core.models.BaseNode
    :no-members:

Node
===========================================================

.. autoclass:: devilry.core.models.Node


Subject
===========================================================

.. autoclass:: devilry.core.models.Subject

Period
===========================================================

.. autoclass:: devilry.core.models.Period

Assignment
===========================================================

Represents one assignment within a given Period_ in a given Subject_. Each
assignment contains one AssignmentGroup_ for each student or group of students
permitted to submit deliveries.

.. _assignment-classifications:

We have three main classifications of assignments:

1. A *old assignment* is a assignment where ``Period.end_time`` is in the past.
2. A *published assignment* is a assignment where ``publishing_time`` is in the past.
3. A *active assignment* is a assignment where ``publishing_time`` is in the
   past and current time is before ``Period.end_time``.


.. autoclass:: devilry.core.models.Assignment


AssignmentGroup
===========================================================

.. autoclass:: devilry.core.models.AssignmentGroup

Delivery
===========================================================

You will normally not create Delivery-objects manually, but rather
use :meth:`Delivery.begin`, :meth:`~Delivery.add_file` and
:meth:`~Delivery.finish` like this::

    delivery = Delivery.begin(myassignmentgroup, currentuser)
    delivery.add_file('hello.txt', ['hello', 'world'])
    delivery.add_file('example.py', ['print "hello world"])
    delivery.finish()

The input to :meth:`add_file` will normally be a file-like object,
but as shown above it can be anything you want.

.. autoclass:: devilry.core.models.Delivery


Feeback
===========================================================

.. autoclass:: devilry.core.models.Feedback


FileMeta
===========================================================

.. autoclass:: devilry.core.models.FileMeta
