.. _user_commonconcepts:

###############
Common concepts
###############


.. _user_specialtermsandconcepts:

**************************
Special terms and concepts
**************************
Devilry has some special terms and concepts. The most important (that cause most confusion) is:

- **Period**: A range of time. Typically a semester or a year.
- **Examiner**: Someone that provides feedback.
- **Group**: Students are always in a (project) group even when they work alone on an assignment.

More details about these and more terms and concepts follows below.


.. _user_node:

Node
====
A Node is a place to organise top-level administrators (I.E.: administrators
responsible for more than one :ref:`user_subject`). Nodes are organised in a tree.
This is very flexible, and can be used to emulate most administrative
hierarchies. A node is often a department, or some other organizational unit,
but the exact use in your local Devilry instance depends on how you choose to
organize administrators in Devilry.


.. _user_subject:

Subject (course)
================
A subject is, as far as Devilry is concerned, a container of :ref:`user_period` s.
In a typical Devilry setup, a Subject is the same as a Course, and each :ref:`user_period` within
the Subject is a semester or year.


.. _user_period:

Period (semester, year, ...)
============================
A period is a limited span of time (I.E: *january to july 2011*) that you give a
name (I.E.: *Spring 2011*). You register assignments on a period, and register
students and examiners on each assignment.


.. _user_group_candidate_student:

Group, Candidate and Student
============================
Students are not registered directly on an assignment. Instead a group is
created, and one or more students is added as Candidates on that group. This
means that project assignments, where students cooperate, is organized exactly
like any other assignment. The only difference is the number of Candidates in
each group.

A Candidate can also have a candidate ID, which is used to identify the student
on anonymous assignments like exams.


.. _user_examiner:

Examiner
========
Examiner is someone that writes feedback. Examiners are often one of these:

- A teacher that corrects their own students. They are usually Period or
  Subject administrator in addition to Examiner.
- A teaching assistant.
- Someone giving anonymous feedback on an exam.

A user becomes examiner when they are assigned as examiner for a group (See
:ref:`user_group_candidate_student`) by an administrator.

.. seealso:: :ref:`The Examiner role <role_examiner>`.


.. _user_feedbackset:

FeedbackSet
===========
FeedbackSets are where comments and deliveries are organized. A FeedbackSet has a deadline(a datetime field) associated
with it, and comments and files belongs to a FeedbackSet. You can see the FeedbackSets as attempts on specific
assignment for a group. The FeedbackSet is not registered directly on an assignment, but on a group which is
registered on the assignment (:ref:`user_group_candidate_student`).


.. _user_groupcomments:

GroupComment
============
GroupComments are the actual deliveries in Devilry. A comment is connected to a FeedbackSet
(see :ref:`user_feedbackset`) and a you can add files to a GroupComment which is considered a delivery.
Technically, a file is a file object associated with what we call a CommentFile, wich again is associated with a
GroupComment.

Note that GroupComments are a way of making deliveries and communicating with other students in your group or the
examiners. Usually, the last comment, or a comment with a file will be considered the delivery.


Special terms in context --- a typical Devilry hierarchy
========================================================

The tree below is an example of a typical Devilry hierarchy for a university named *Duckburgh University* with
the special terms in brackets.


- Duckburgh University [:ref:`user_node`]
    - Department of Physics [:ref:`user_node`]
        - PHYS 101 --- Introduction to physics [:ref:`user_subject`]
            - Spring 2011 [:ref:`user_period`]
                - Assignment one
                    - Peter Pan and Wendy [:ref:`user_group_candidate_student`]
                        - FeedbackSet first attempt (deadline feb. 27 2012 19:30) [:ref:`user_feedbackset`]
                            - Delivery 1 [:ref:`user_groupcomments`]
                                - Delivery file
                    - Captain Hook [:ref:`user_group_candidate_student`]
                        - FeedbackSet second attempt (deadline mar. 12 2012 11:45) [:ref:`user_feedbackset`]
                            - Delivery 3 [:ref:`user_groupcomments`]
                                - Delivery file
                        - FeedbackSet first attempt (deadline feb. 28 2012 12:30) [:ref:`user_feedbackset`]
                            - Delivery 2 [:ref:`user_groupcomments`]
                                - Delivery file
                            - Delivery 1 [:ref:`user_groupcomments`]
                                - Delivery file
                    - John Doe [:ref:`user_group_candidate_student`]
                        - FeedbackSet (deadline feb. 25 2012 23:35) [:ref:`user_feedbackset`]
                            - Delivery 1 [:ref:`user_groupcomments`]
                                - Delivery file
            - Spring 2012 [:ref:`user_period`]
            - Spring 2013 [:ref:`user_period`]
        - PHYS 302 --- Advanced physics [:ref:`user_subject`]
        - ...
    - Department of Informatics [:ref:`user_node`]
        - INF 101 --- Introduction to programming [:ref:`user_subject`]
        - INF 102 --- Objectoriented programming [:ref:`user_subject`]
        - ...
    - ...


Simple visual representation of the delivery workflow
=====================================================
Here's a simple workflow represented visually from the students standpoint. This does not differ that much from
examiners and admins standpoints when on the delivery feed page.

1. Student asks the examiner a question
2. Examiner answers
3. Student submits their delivery
4. The deadline expires
5. Examiner corrects the assignment


.. image:: images/simple_delivery_workflow.png


