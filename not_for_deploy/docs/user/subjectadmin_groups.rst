############################################################
How to administer project groups (students that collaborate)
############################################################


*********************
Concepts and features
*********************
Devilry is designed with cooperative deliveries in mind.

- Students are *always* in a group even when they work alone.
- Course admins can safely create and split up project groups at any time.
- You can :ref:`enable students to create project groups on their own <enable_students_to_create_project_groups>`.
- Groups are created and managed per assignment. This means that changing a
  group on one assignment does not affect that group on another assignment.
  You can copy groups from another assignment when you create a new assignment.
- Students can be organized in groups even after they have made deliveries and
  been given feedback. They their respective groups are simply merged into
  a single group with all deliveries and feedback. The last feedback (if any)
  is made the active feedback.


.. _enable_students_to_create_project_groups:

************************************************************
How to enable students to create project groups on their own
************************************************************
If you want to allow students to form project groups on their own, you have to
enable this option on the assignment:

1. Go to the overview page for an assignment where you have administrator rights.
2. Click any of the edit buttons in the sidebar to your left, except the edit button for *Grading system*.
3. Edit the options in the *Allow students to form project groups* section.

.. note::

    To see how students form project groups on their own, see
    :doc:`student_groups`. You should refer your students to that guide when you
    ask them to form their own groups. Devilry does not notify students when you
    enable this feature.


.. note::

    This is not as intuitive as it should be. It will be made more intuitive in
    the future.



**************************************
How to manually create a project group
**************************************

1. Open the students overview on the relevant assignment.
2. Select two or more groups/students.
3. Select *Create project group*.

Exactly what this means is explained when you click *Create project group*, and
you have to confirm before the group is created. In short, 


************************************
How to remove a student from a group
************************************
Students can not leave groups on their own (yet). So an admin has to manage that:

1. Open the students overview on the relevant assignment.
2. Select the group.
3. Click the red minus button on the right hand side of the student you wish to remove from the group.

This will do the following:
- Create a copy of the group with *all* deliveries and feedback, even
  deliveries made by other students before the student you are removing joined
  the group.
- Add the student you are removing to the copy of the original group.
