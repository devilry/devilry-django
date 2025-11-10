=============================
Migrating from 6.4.1 to 6.4.2
=============================


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########

- Change to how errors from background tasks are reported. They now support more than just logs, but still default to
  logging.


Update devilry to 6.4.2
#######################

Update the devilry version to ``6.4.2`` as described in :doc:`../update`.

If you want to use Sentry for error reporting from background tasks, follow the instructions in :doc:`../sentry`.
