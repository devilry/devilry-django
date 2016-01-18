#######################################################
:mod:`devilry_group` --- Devilry group models and views
#######################################################

The ``devilry_group`` module handles the delivery of assignments by students.


***************************
About the devilry group app
***************************
The devilry_group app uses a comment-based feedbackfeed system
for delivering assignments and recieiving feedback on those deliveries.

- The feedbackfeed gather all information about a an assignment in one place, and
  makes it easy for students, examiners and admins to communicate.
- The feedbackfeed consists of one or more feedbacksets.
- A feedbackset may or may not have a deadline and zero or more comments belonging to it.
- Student, examiners and admins can write comments to the feedbackset.
- If a student fails an assignment, and is given another chance, a new feedbackset
  is created with a new deadline.
- All events show up in the feed in the order they happen, when a deadline is created,
  a comment is posted, a deadline ends and the status of the grading. You will also have direct access
  to download the files delivered.


*****************************
How does the feedbackset work
*****************************
asd


*************
Datamodel API
*************

.. currentmodule:: devilry.devilry_group.models

.. automodule:: devilry.devilry_group.models
    :members:

*********
Views API
*********

.. currentmodule:: devilry.devilry_group.cradmin_feedbackfeed_base

.. currentmodule:: devilry.devilry_group.feedbackfeed_student

.. currentmodule:: devilry.devilry_group.feedbackfeed_examiner

.. currentmodule:: devilry.devilry_group.feedbackfeed_admin

.. automodule:: devilry.devilry_group.views.cradmin_feedbackfeed_base
    :members:

.. automodule:: devilry.devilry_group.views.feedbackfeed_student
    :members:

.. automodule:: devilry.devilry_group.views.feedbackfeed_examiner
    :members:

.. automodule:: devilry.devilry_group.views.feedbackfeed_admin
    :members:

*************
Writing tests
*************
In most cases, just using ``model_mommy`` (mommy.make) should be enough,
but we provide some factory-methods that makes this a bit easier.

Example - create a group with two "tries"::

    testgroup = mommy.make('core.AssignmentGroup',
                           parentnode__first_deadline=timezone.now() - timedelta(days=10)
    devilry_group_mommy_factories.feedbackset_first_try_published(
        group=testgroup,
        grading_points=10,
        deadline_datetime=timezone.now() - timedelta(days=10),  # Not required - defaults not timezone.now()
        is_last_in_group=False)
    devilry_group_mommy_factories.feedbackset_new_try_published(
        group=testgroup,
        grading_points=20,
        is_last_in_group=True)



.. currentmodule:: devilry.devilry_group.devilry_group_mommy_factories

.. automodule:: devilry.devilry_group.devilry_group_mommy_factories
    :members:
