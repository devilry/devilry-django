==================
Migrating to 6.7.0
==================

.. warning:: Always update one version at a time. Do not skip versions unless it is explicitly stated in the migration guide.


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.

What's new?
###########
- Fix: Better authentication error handling.
- Fix: Add counters to selected items in multiselect-views.
- Fix: Grading configuration gets reset when plugin changes.
- Fix: Dependency cleanup.


Update devilry
##############

1. Remove `cradmin_legacy` dependencies in your `devilrydeploy/requirements.txt` (and `django_cradmin` if in requirements.txt).
2. Update the devilry version to ``6.7.0`` as described in :doc:`../update`.
