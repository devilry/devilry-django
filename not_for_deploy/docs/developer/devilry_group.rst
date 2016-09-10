#######################################################
:mod:`devilry_group` --- Devilry group models and views
#######################################################

The ``devilry_group`` module handles the delivery of assignments by students.


***************************
About the devilry group app
***************************
The devilry_group app uses a comment/event-based feedbackfeed system
for delivering assignments and recieiving feedback on those deliveries.

- The feedbackfeed gather all information about a an assignment in one place, and
  makes it easy for students, examiners and admins to communicate.
- The feedbackfeed consists of one or more feedbacksets.
- A feedbackset may or may not have a deadline and zero or more comments belonging to it.
- Students, examiners and admins can write comments to the feedbackset.
- If a student fails an assignment, and is given another chance, a new feedbackset
  is created with a new deadline.
- All events show up in the feed in the order they happen, when a deadline is created,
  a comment is posted, a deadline ends and the status of the grading. You also have direct access
  to download the files delivered from the feedbackfeed.


**********************
What is a FeedbackSet?
**********************
The FeedbackSet has a foreignkey to an AssignmentGroup and groups all information about a specific deadline for
the Assignment the AssignmentGroup is associated with. A new FeedbackSet is created for each deadline e.g. regarding new
attempts if the student failed on the first delivery. See the model API below.


*************
Datamodel API
*************

.. currentmodule:: devilry.devilry_group

.. automodule:: devilry.devilry_group.models
    :members:


*********
Views API
*********

.. currentmodule:: devilry.devilry_group.views

.. automodule:: devilry.devilry_group.views.cradmin_feedbackfeed_base
    :members:


Examiner view
=============

.. py:currentmodule:: devilry.devilry_group.views.examiner

.. automodule:: devilry.devilry_group.views.examiner.feedbackfeed_examiner
    :members:


Admin view
==========

.. currentmodule:: devilry.devilry_group.views

.. automodule:: devilry.devilry_group.views.admin.feedbackfeed_admin
    :members:


Student view
============

.. currentmodule:: devilry.devilry_group.views

.. automodule:: devilry.devilry_group.views.student.feedbackfeed_student
    :members:



*********************************************
Using ListBuilder to render the feedbackfeed.
*********************************************

.. currentmodule:: devilry.devilry_cradmin.devilry_listbuilder

.. automodule:: devilry.devilry_cradmin.devilry_listbuilder.feedbackfeed_timeline
    :members:


*************
Writing tests
*************
In most cases, just using ``model_mommy`` (mommy.make) should be enough,
but we provide some factory-methods that makes this a bit easier.

Example - create a group with two "attempts"

.. code-block:: python

    testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__first_deadline=timezone.now() - timedelta(days=10)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup,
            grading_points=10,
            deadline_datetime=timezone.now() - timedelta(days=10),
            is_last_in_group=False)
        devilry_group_mommy_factories.feedbackset_new_attempt_published(
            group=testgroup,
            grading_points=20,
            is_last_in_group=True)



.. currentmodule:: devilry.devilry_group.devilry_group_mommy_factories

.. automodule:: devilry.devilry_group.devilry_group_mommy_factories
    :members:
