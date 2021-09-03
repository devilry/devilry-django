=============================
Migrating from 5.1.0 to 5.2.0
=============================


What's new
##########

- Updated to Django 3.2.* LTS
- WCAG: H2-tag is now used instead of h3 on account page.
- Admin: If assignments exists for a semester, the admin will be reminded to add students to the assignments when students are added/imported to the semester.
- Comment notifications: If no examiners are assigned to a group, the course and semester administrators will receive notifications when students post comments.
- Deadline management: Admins can no longer move deadlines for graded attempts.
- Deadline management: Suggestions always use midnight as the time for the suggested deadline.
- Deadline calendar widget: Defaults to 23:59 instead of the current time.


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 5.2.0
#######################

Update the devilry version to ``5.2.0`` as described in :doc:`../update`.
