==================
Migrating to 6.6.1
==================

.. warning:: Always update one version at a time. Do not skip versions unless it is explicitly stated in the migration guide.


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.

Fixes
#####

- Bugfix: Expected format of `Status.plugin_data` caused an error when accessing the detail-view for old statuses. Migrate plugin_data for the select_assignments 
qualifies-for-exam plugin from a list to a dict.


Update devilry
##############

Update the devilry version to ``6.6.1`` as described in :doc:`../update`.
