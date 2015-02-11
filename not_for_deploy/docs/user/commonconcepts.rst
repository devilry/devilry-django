.. _commonconcepts:

=====================================
Common concepts
=====================================


Localization
###############################
Devilry can be translated to multiple languages and dialects. Each dialect
makes Devilry feel more at home in its environment. A dialect translates
special terms (see :ref:`specialtermsandconcepts`). This is important to
understand when reading this documentation, because we use the special terms
throughout the documentation, not the dialects.


.. _specialtermsandconcepts:

Special terms and concepts
###############################
Devilry has some special terms and concepts. The most important (that cause most confusion) is:

- **Period**: A range of time. Typically a semester or a year.
- **Examiner**: Someone that provides feedback.
- **Group**: Students are always in a (project) group even when they work alone on an assignment.

More details about these and more terms and concepts follows below.


.. _node:

Node
======================================================
A Node is a place to organise top-level administrators (I.E.: administrators
responsible for more than one :ref:`subject`). Nodes are organised in a tree.
This is very flexible, and can be used to emulate most administrative
hierarchies. A node is often a department, or some other organizational unit,
but the exact use in your local Devilry instance depends on how you choose to
organize administrators in Devilry.


.. _subject:

Subject (course)
======================================================
A subject is, as far as Devilry is concerned, a container of :ref:`Periods
<period>`. In a typical Devilry setup, a Subject is the same as a Course, and
each :ref:`Period <period>` within the Subject is a semester or year.


.. _period:

Period (semester, year, ...)
======================================================
A period is a limited span of time (I.E: *january to july 2011*) that you give a
name (I.E.: *Spring 2011*). You register assignments on a period, and register
students and examiners on each assignment.


.. _group_candidate_student:

Group, Candidate and Student
======================================================
Students are not registered directly on an assignment. Instead a group is
created, and one or more students is added as Candidates on that group. This
means that project assignments, where students cooperate, is organized exactly
like any other assignment. The only difference is the number of Candidates in
each group.

A Candidate can also have a candidate ID, which is used to identify the student
on anonymous assignments like exams.

.. seealso:: :ref:`The Student role <role_student>`.


.. _deadline:

Deadline
======================================================
Deadlines are individual for each group. They are organized *below* a Group in
the Devilry hierarchy. In other words: Each Group has one or more deadlines.


.. _examiner:

Examiner
======================================================
Examiner is someone that writes feedback. Examiners are often one of these:

- A teacher that corrects their own students. They are usually Period or
  Subject administrator in addition to Examiner.
- A teaching assistant.
- Someone giving anonymous feedback on an exam.

A user becomes examiner when they are assigned as examiner for a group (See
:ref:`group_candidate_student`) by an administrator.

.. seealso:: :ref:`The Examiner role <role_examiner>`.



Special terms in context --- a typical Devilry hierarchy
========================================================

The tree below is an example of a typical Devilry hierarchy for a university named *Duckburgh University* with
the special terms in brackets.

- Duckburgh University [:ref:`node`]
    - Department of Physics [:ref:`node`]
        - PHYS 101 --- Introduction to physics [:ref:`subject`]
            - Spring 2011 [:ref:`period`]
                - Assignment one
                    - Peter Pan and Wendy [:ref:`group_candidate_student`]
                        - Deadline feb. 27 2012 19:30 [:ref:`deadline`]
                            - Delivery 1
                    - Captain Hook [:ref:`group_candidate_student`]
                        - Deadline mar. 12 2012 11:45 [:ref:`deadline`]
                            - Delivery 3
                        - Deadline feb. 28 2012 12:30 [:ref:`deadline`]
                            - Delivery 2
                            - Delivery 1
                    - John Doe [:ref:`group_candidate_student`]
                        - Deadline feb. 25 2012 23:35 [:ref:`deadline`]
                            - Delivery 1
            - Spring 2012 [:ref:`period`]
            - Spring 2013 [:ref:`period`]
        - PHYS 302 --- Advanced physics [:ref:`subject`]
        - ...
    - Department of Informatics [:ref:`node`]
        - INF 101 --- Introduction to programming [:ref:`subject`]
        - INF 102 --- Objectoriented programming [:ref:`subject`]
        - ...
    - ...

