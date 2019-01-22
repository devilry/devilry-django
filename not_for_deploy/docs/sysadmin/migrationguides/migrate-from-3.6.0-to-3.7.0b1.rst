===============================
Migrating from 3.6.0 to 3.7.0b1
===============================


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


Fixes and tweaks
################

- New email framework with error handling. Supports resending of failed messages, saves errors for later debugging and
  manual mail-resending available to sysadmins.
- Downloadable student results on semester.
- Added list counters for course and student listing views.
- Fixed group-status filter. This was caused by a filter that had been overlooked when we moved on to simple
  data-caching for groups.
- Tested on Postgres 11.1.


Update devilry to 3.7.0b1
#########################

Update the devilry version to ``3.7.0b1`` as described in :doc:`../update`.
