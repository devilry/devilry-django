===================================
Migrating from 5.2.0rc1 to 5.2.0rc2
===================================


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


Update devilry to 5.2.0rc2
##########################

Uninstall django_errortemplates with PIP **between** step 2 and 3 in the :doc:`../update`::

    $ cd ~/devilrydeploy
    $ venv/bin/pip uninstall django_errortemplates

Update the devilry version to ``5.2.0rc2`` as described in :doc:`../update`.
