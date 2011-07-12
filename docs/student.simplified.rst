.. _apps.student.simplified:

=================================================================================
:mod:`devilry.apps.student.simplified` --- Simplifed API for students
=================================================================================

The student simplified API. This API is a simplified wrapper of
:ref:`devilry.apps.core.models` for students. Every action requires
the given user to be student on the object being manipulated.

Simplified API
==============

Subject
#########################################################
.. autoclass:: devilry.apps.student.simplified.SimplifiedSubject
    :inherited-members: 

Period
#########################################################
.. autoclass:: devilry.apps.student.simplified.SimplifiedPeriod
    :inherited-members: 

Assignment
#########################################################
.. autoclass:: devilry.apps.student.simplified.SimplifiedAssignment
    :inherited-members: 

AssignmentGroup
#########################################################
.. autoclass::  devilry.apps.student.simplified.SimplifiedAssignmentGroup
    :inherited-members: 

Deadline
#########################################################
.. autoclass::  devilry.apps.student.simplified.SimplifiedDeadline
    :inherited-members: 

Delivery
#########################################################
.. autoclass::  devilry.apps.student.simplified.SimplifiedDelivery
    :inherited-members: 

StaticFeedback
#########################################################
.. autoclass::  devilry.apps.student.simplified.SimplifiedStaticFeedback
    :inherited-members: 

FileMeta
#########################################################
.. autoclass::  devilry.apps.student.simplified.SimplifiedFileMeta
    :inherited-members: 
