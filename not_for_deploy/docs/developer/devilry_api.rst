################################################################
:mod:`devilry_api` --- Devilry API models, serializers and views
################################################################

The ``devilry_api`` module is a RESTFUL api for devilry


#################
About devilry api
#################
The devilry_api is built on django rest framework and documented with swagger.
For swagger docs see /api/docs.


##################
What is an APIKey?
##################
The APIKey has a foreign key to a user and stores information of its purpose and permission level.
It also has a key type which tells how long a key last from it's created datetime.
There are three types of permission classes, admin-, examiner- and student permission.
Each permission class has 3 types of permission levels, no permission which is the default, read only and write.


#########
Datamodel
#########

.. py:currentmodule:: devilry.devilry_api.models

.. automodule:: devilry.devilry_api.models
    :members:


##############
Assignment API
##############

.. py:currentmodule:: devilry.devilry_api.assignment

.. automodule:: devilry.devilry_api.assignment.views.assignment_base
    :members:


Student
=======
The assignment student api will list all assignments which a student is and has been a part of.

.. automodule:: devilry.devilry_api.assignment.views.assignemnt_student
    :members:


Examiner
========
The assignment examiner api will list all assignments which an examiner has access to.

.. automodule:: devilry.devilry_api.assignment.views.assignment_examiner
    :members:


Period admin
============
**Comming soon**
The assignment period admin api will list all assignments which a period admin has access to.
In addition to that a period admin will also be able to:
* Create an assignment with anonimization mode off.
* update all properties except anonimization mode.
* Delete an assignment if there is no child content other than basic initialization content,
  for instance a period admin should not be able to delete an assignment if there is a comment on a feedback set.
Other features that we should consider:
* Dry runs show whats being deleted?


Subject admin
=============
**Comming soon**
Has same privileges as period admin, but in addition to that a subject admin has also access to semi anonymous exams.


####################
Assignment Group API
####################

.. py:currentmodule:: devilry.devilry_api.assignment_group

.. automodule:: devilry.devilry_api.assignment.views.assignmentgroup_base
    :members:


Student
=======
The assignment group student api will list all assignment groups which a student is and has been a part of.

.. automodule:: devilry.devilry_api.assignemnt_group.views.assignemntgroup_student
    :members:


Examiner
========
The assignment group examiner api will list all assignments groups which an examiner has access to.

.. automodule:: devilry.devilry_api.assignment_group.views.assignmentgroup_examiner
    :members:


Period admin
============
**Comming soon**
The assignment group period admin api will list all assignment groups which a period admin has access to.
In additon to that a period admin will also be able to:
* Create assignment group.
* Add examiners and students to assignment group.
* Delete assignment group if there is no students in assignment group.


Subject admin
=============
**Comming soon**
Has same privileges as period admin, but in addition to that a subject admin has also access to semi anonymous exams.


###############
Feedbackset API
###############

.. py:currentmodule:: devilry.devilry_api.feedbackset

.. automodule:: devilry.devilry_api.feedbackset.views.feedbackset_base
    :members:


Student
=======
The feedbackset student api will list all feedback sets which a student has access to.

.. automodule:: devilry.devilry_api.feedbackset.views.feedbackset_student
    :members:


Examiner
========
The feedbackset examiner api will list all feedback sets which an exminer has access to.
In addition to that an examiner will also be able to:
* Create a new feedbackset (if the old feedbackset has expired and grading is published?)
* Publish a feedbackset with grading points. **Cooming soon**

.. automodule:: devilry.devilry_api.feedbackset.views.feedbackset_examiner
    :members:


Period admin
============
**Comming soon**
The feedbackset period admin api will list all feedbacksets which a period admin has access to.
In addition to that a period admin will also be able to:
* Create feedbackset.
* Update feedbackset.


Subject admin
=============
**Comming soon**
Has same previleges as period admin, but in addition to that a subject admin has also access to semi anonymous exams.


#############
Group Comment
#############

.. py:currentmodule:: devilry.devilry_api.group_comment

.. automodule:: devilry.devilry_api.group_comment.views.groupcomment_base
    :members:


Student
=======
In the group comment student api a student will be able to:
* View all comments which is Visible to everyone.
* Post comments which is visible to everyone and not part_of_grading comments.

.. automodule:: devilry.devilry.feedbackset.views.groupcomment_student
    :members:


Examiner
========
In the group comment examiner api an examiner will be able to:
* View all comments but not other examiners private comments.
* Post comments which is either visible to everyone, examiners and admins or private for drafts.

.. automodule:: devilry.devilry.feedbackset.vies.groupcomment_examiner
    :members:


Period admin
============
**Comming soon**
In the group comment period admin api a period admin should be able to:
* View all comments, but not an examiners drafted comments.
* Post comments with visibility to everyone or visible to examiners and admins.

Subject admin
=============
**Comming soon**
Has same previleges as period admin, but in addition to that a subject admin has also access to semi anonymous exams.
