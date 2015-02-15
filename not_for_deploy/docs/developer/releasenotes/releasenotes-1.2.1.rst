====================================
1.2.1 release notes
====================================

.. seealso:: :devilrydeploy:`Migration guide for sysadmins <migrationguides/1.2.1.html>`


##############################
Major changes
##############################

Semantic changes
================
Administrators are no longer implicitly examiner. They must make themself examiner if they want
to provide feedback to students. We have made it easy to make yourself examiner:

- An option when creating an assignment.
- Administrators can edit examiners on the period/semester.
- When browsing a group (student), you get a button to make yourself examiner if you are
  not already.


A complete rewrite of the deployment system
===========================================
We have split our deployment scripts (for system administrators) into a separate repository.
The repository includes a Chef DevOps setup that should simplify the work of system admins
greatly. It also includes a much better setup for those who do not wish to use Chef. See
http://devilry-deploy.readthedocs.org/ for more information.


New subject admin UI
====================
A completely new user interface for subject (course) administrators. The UI has more or less all of
the features of the old UI, but it is far more user-friendly and optimized for common task.
Some highlights:


Create new assignment wizard
----------------------------
Smart and efficient *create new assignment* wizard. The wizard sets up an assignnent, adds students
to the assignment and assigns examiners to the students with very little input needed.

The wizard is smart and tries to suggest values when you create assignments. It automatically
suggests names of assignments based on previous assignments. So if you name your first assignment
*Assignment 1*, it will suggest *Assignment 2* for your next assignment.

The wizard also autodetects regularly repeating assignments, and suggests publishing time and
submission dates based on regular intervals. This means that if you have weekly deliveries,
you will only have to setup the submission and publishing times on the first 2 weeks, and Devilry
will suggest sane defaults for the rest. It even works if you have a break of a week or 2, because
Devilry uses the most common interval for all your assignments.

For those who like to set up many assignments, the wizard has a shortcut after each assignment is
created, that lets you re-run the wizard using the same settings. Combined with the autodetection
described above, this means that you can setup many assignments in a very efficient manner.


Semester/period overview
------------------------
An overview, very similar to the one in the old UI, but it is faster and has some new features.
Autodetects problems with missing students. Supports export to Office Open XML (MS Excel), CSV, JSON,
XML, YAML and REST API.


Logging of all dangerous actions
--------------------------------
We log all dangerous actions in the new UI, like deletion, renaming, moving deadline, and so on.
The log-records include the action performed, with IDs and names, the user who made the change,
and the time the change occurred. We also log failed dangerous actions.


New system for marking qualified for final exam
-----------------------------------------------
Far more user-friendly and plugin based, so it is easy to extend.

Edit examiners and students on semesters/periods
------------------------------------------------
Admins can manage their own students and examiners. They can tag students and examiners, and
use those tags to automatch students and examiners on all assignments.

Deadline manager
----------------
A full featured deadline manager that gives you full control over all your deadlines, and
the students on each deadline. Among many other features, it supports moving deadlines (which
several users have requested).

Interractive guide system
-------------------------
A guide that stays at your right hand side and guides you through the UI.
We only have a guide that helps users creating new assignments, but we will add guides
when users tell us what they need help understanding.

Smarter statuses
----------------
Groups (students) are no longer closed or open. Instead they have smarter statuses, like:
*Waiting for feedback*, *Waiting for deliveries*, *Corrected*, and so on.

Statistics about examiners on an assignment
-------------------------------------------
Charts and numbers that should help admins keep track of their examiners.
Please let us know if you have suggestions for more numbers or charts in this
view, or if you have ideas for making it better.


New node admin UI
=================
Because the old admin interface was for both node and subject administrator, we had to
make a new UI for node administrators when we replaced it. This UI is not very powerful
in this release, but we plan to improve it gradually in cooperation with its users.
