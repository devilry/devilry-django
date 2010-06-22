.. _ref-devilry.core.models:

=========================================================
:mod:`devilry.core.models` --- Devilry core datastructure
=========================================================


BaseNode and children
=====================

Most of the core models inherit from the BaseNode class, and we refer to them
all as nodes. Since we also have a class named ``Node``, this might be a bit
confusing, but the context should always make the distinction clear.


BaseNode
--------

.. autoclass:: devilry.core.models.BaseNode
    :members:
    :show-inheritance:


Node
----

.. autoclass:: devilry.core.models.Node
    :members:
    :show-inheritance:


Subject
-------

.. autoclass:: devilry.core.models.Subject
    :members:
    :show-inheritance:

Period
------

.. autoclass:: devilry.core.models.Period
    :members:
    :show-inheritance:

Assignment
----------

.. autoclass:: devilry.core.models.Assignment
    :members:
    :show-inheritance:


Other
=====

These models do not inherit from ``BaseNode``, but they are still a part of the
hierarchy through their connection to ``Assignment`` (direct or indirect).

AssignmentGroup
---------------

.. autoclass:: devilry.core.models.AssignmentGroup
    :members:
    :show-inheritance:

Feeback
-------

.. autoclass:: devilry.core.models.Feedback
    :members:
    :show-inheritance:

Delivery
--------

.. autoclass:: devilry.core.models.Delivery
    :members:
    :show-inheritance:


FileMeta
--------

.. autoclass:: devilry.core.models.FileMeta
    :members:
    :show-inheritance:
