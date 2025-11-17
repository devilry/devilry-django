=============================
Migrating from 6.4.2 to 6.4.3
=============================


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########

- Fix a bug where batchframework tasks did not re-raise exceptions correctly, causing the tasks to be marked as successful in the BatchOperation  table even when they failed.
- Add more options related to testing serverside error reporting. See the _Verifying the setup_ section in :doc:`../rq` for details.


Update devilry to 6.4.3
#######################

Update the devilry version to ``6.4.3`` as described in :doc:`../update`.

If you want to use Sentry for error reporting from background tasks, follow the instructions in :doc:`../sentry`.
