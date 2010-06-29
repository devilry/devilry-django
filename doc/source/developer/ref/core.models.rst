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
    :no-inherited-members:

Node
===========================================================

.. autoclass:: devilry.core.models.Node
    :members:
    :inherited-members:
    :show-inheritance:


Subject
===========================================================

.. autoclass:: devilry.core.models.Subject
    :members:
    :inherited-members:
    :show-inheritance:

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
    :members:
    :inherited-members:
    :show-inheritance:
    :member-order: bysource


AssignmentGroup
===========================================================

.. autoclass:: devilry.core.models.AssignmentGroup
    :members:
    :inherited-members:

Feeback
===========================================================

.. autoclass:: devilry.core.models.Feedback
    :members:
    :inherited-members:

Delivery
===========================================================

.. autoclass:: devilry.core.models.Delivery
    :members:
    :inherited-members:


FileMeta
===========================================================

.. autoclass:: devilry.core.models.FileMeta
    :members:
    :inherited-members:
