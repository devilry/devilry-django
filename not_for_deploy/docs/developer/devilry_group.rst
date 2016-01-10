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
