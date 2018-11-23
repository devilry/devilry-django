============================================
Migrating from 3.5.0 to 3.5.1 (NOT RELEASED)
============================================

..note::

    NOT RELEASED


Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.

Fixes and tweaks
################

Students, examiners and admins:

 - Feedback feed: Previously, merge history was excluded if no public comments existed. We now include all types of comments. Note that merged
   feedbackset with "internal" notes will only be visible to examiners and admin, and will not clutter up the feedbackfeed of a student.

 - Feedback feed: Merge history is expanded by default.

 - Students that have had their assignment corrected but the deadline has not yet expired will be shown with
   status "Waiting for deliveries" since they can still upload files and new comments. When the deadline expires, the
   status will switch to the grading received.

 - Feedbackset status affected by "merge history" feedbacks fixed. This was an issue with a PostgreSQL trigger.


Examiners:

 - Examiners can not move the deadline of a student/group if the assignment has been corrected. They will need to either
   edit the grading or give the student/group a new attempt.


Examiners and admins:
 - Previously, a deadline had to be after the latest previous deadline. Deadlines can now be moved back and forth, but
   no earlier than the current time.



Update devilry to 3.5.1
#######################

Update the devilry version to ``3.5.1`` as described in :doc:`../update`.

After updating, you need to run::

    $ venv/bin/python manage.py ievvtasks_customsql -i -r
