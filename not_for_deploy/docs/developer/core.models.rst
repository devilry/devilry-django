.. _devilry.apps.core.models:

===============================================================
:mod:`devilry.apps.core.models` --- Devilry core datastructure
===============================================================


.. image:: images/devilry.core.models.1.png

.. image:: images/devilry.core.models.2.png

(edit the images umldiagram1_ and umldiagram2_ using yuml.me)

.. _umldiagram1: http://yuml.me/diagram/plain;dir:LR;scale:80;/class/edit/[Node]++1-subjects >*[Subject], [Node]++0-child-nodes >*[Node], [Subject]++1-periods >*[Period], [Period]++1-assignments >*[Assignment], [Assignment]++1-assignmentgroups >*[AssignmentGroup]
.. _umldiagram2: http://yuml.me/diagram/scruffy/class/edit/%5BAssignmentGroup%5D++1-deadlines%20%3E*%5BDeadline%5D,%20%5BAssignmentGroup%5D++1-candidates%20%3E*%5BCandidate%5D,%20%5BDelivery%5D++1-staticfeedbacks%20%3E*%5BStaticFeedback%5D,%20%5BDelivery%5D++1-filemetas%20%3E*%5BFileMeta%5D,%20%5BDeadline%5D++1-deliveries%20%3E*%5BDelivery%5D,%20%5BDelivery%5D++1-delivered_by%20%3E1%5BCandidate%5D

Functions and attributes
#########################################################

.. automodule:: devilry.apps.core.models.model_utils
    :members: pathsep, splitpath
    :no-members:


BaseNode
#########################################################

.. autoclass:: devilry.apps.core.models.BaseNode
    :no-members:


AbstractIsAdmin
#########################################################

.. autoclass:: devilry.apps.core.models.AbstractIsAdmin


AbstractIsExaminer
#########################################################

.. autoclass:: devilry.apps.core.models.AbstractIsExaminer


Node
#########################################################

A node at the top of the navigation tree. It is a generic element used to
organize administrators. A Node can be organized below another Node, and it
can only have one parent.

Let us say you use Devilry within two departments at *Fantasy University*;
informatics and mathematics. The university has an administration, and each
department have their own administration. You would end up with this
node-hierarchy:

    - Fantasy University
        - Department of informatics
        - Department of mathematics

.. autoclass:: devilry.apps.core.models.Node


Subject
#########################################################

A subject is a course, seminar, class or something else being given
regularly. A subject is further divided into periods.

.. autoclass:: devilry.apps.core.models.Subject

Period
#########################################################

A Period is a limited period of time, like *spring 2009*, *week 34 2010* or
even a single day.

.. autoclass:: devilry.apps.core.models.Period


RelatedUserBase
#########################################################

Base class for :class:`devilry.apps.core.models.RelatedStudent` and :class:`devilry.apps.core.models.RelatedExaminer`.

.. autoclass:: devilry.apps.core.models.relateduser.RelatedUserBase


RelatedStudent --- Student on a period
#########################################################

A RelatedStudent is a student *related* to a :class:`devilry.apps.core.models.Period`.

.. autoclass:: devilry.apps.core.models.RelatedStudent

RelatedExaminer --- Examiner on a period
#########################################################

A RelatedExaminer is an examiner *related* to a :class:`devilry.apps.core.models.Period`.

.. autoclass:: devilry.apps.core.models.RelatedExaminer

Assignment
#########################################################

Represents one assignment within a given Period_ in a given Subject_. Each
assignment contains one AssignmentGroup_ for each student or group of students
permitted to submit deliveries.

.. _assignment-classifications:

We have three main classifications of assignments:

1. A *old assignment* is a assignment where ``Period.end_time`` is in the past.
2. A *published assignment* is a assignment where ``publishing_time`` is in the past.
3. A *active assignment* is a assignment where ``publishing_time`` is in the
   past and current time is before ``Period.end_time``.


.. autoclass:: devilry.apps.core.models.Assignment

Examiner
#########################################################

.. autoclass:: devilry.apps.core.models.Examiner
    :no-members:


Candidate
#########################################################

.. autoclass:: devilry.apps.core.models.Candidate
    :no-members:

AssignmentGroup
#########################################################

.. autoclass:: devilry.apps.core.models.AssignmentGroup

AssignmentGroupTag
#########################################################

.. autoclass:: devilry.apps.core.models.AssignmentGroupTag


Deadline
#########################################################

Each `AssignmentGroup`_ have zero or more deadlines.

.. autoclass:: devilry.apps.core.models.Deadline


Delivery
#########################################################


Examples
========

Simple example::

    assignmentgroup = AssignmentGroup.objects.get(id=1)
    assignmentgroup.deliveries.create(delivered_by=student1,
                                      successful=True)


More advanced example::

    assignmentgroup = AssignmentGroup.objects.get(id=1)
    delivery = assignmentgroup.deliveries.create(delivered_by=student1,
                                                 successful=False)
    delivery.add_file('test.py', ['print', 'hello world'])
    delivery.add_file('test2.py', ['print "hi"'])
    delivery.successful = True
    delivery.save()

The input to :meth:`add_file` will normally be a file-like object,
but as shown above it can be anything you want.


Delivery API
============

.. autoclass:: devilry.apps.core.models.Delivery


StaticFeedback
#########################################################

.. autoclass:: devilry.apps.core.models.StaticFeedback


FileMeta
#########################################################

.. autoclass:: devilry.apps.core.models.FileMeta



DevilryUserProfile
#########################################################

**See also**: :ref:`userobj`.

.. autoclass:: devilry.apps.core.models.DevilryUserProfile


.. _django.db.models.SlugField: http://docs.djangoproject.com/en/dev/ref/models/fields/#slugfield
.. _django.db.models.CharField: http://docs.djangoproject.com/en/dev/ref/models/fields/#charfield
.. _django.db.models.ForeignKey: http://docs.djangoproject.com/en/dev/ref/models/fields/#foreignkey
.. _django.db.models.ManyToManyField: http://docs.djangoproject.com/en/dev/ref/models/fields/#manytomanyfield
.. _django.db.models.DateTimeField: http://docs.djangoproject.com/en/dev/ref/models/fields/#datetimefield
.. _django.db.models.BooleanField: http://docs.djangoproject.com/en/dev/ref/models/fields/#booleanfield
.. _django.db.models.OneToOneField: http://docs.djangoproject.com/en/dev/ref/models/fields/#onetoonefield
.. _django.db.models.TextField: http://docs.djangoproject.com/en/dev/ref/models/fields/#textfield
.. _django.contrib.auth.models.User: http://docs.djangoproject.com/en/dev/topics/auth/#users
