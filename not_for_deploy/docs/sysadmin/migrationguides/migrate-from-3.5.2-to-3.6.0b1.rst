======================================
Migrating from 3.5.2 to 3.6.0b1 (BETA)
======================================

.. note::
    Beta

Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.

Fixes and tweaks
################

Superuser:
 - Fixed management command `devilry_periodsetrelatedstudents` overriding the active field on relatedusers.
 - Management command `devilry_subjectadd` now supports the created subject being added to multiple permission groups.
 - Tweaks to `devilry_delete_inactive_users` and `devilry_delete_periods` management commands.


Update devilry to 3.6.0b1
#########################

Update the devilry version to ``3.6.0b1`` as described in :doc:`../update`.
