===========================================
Migrating from 3.3.4 to 3.6.5
===========================================


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########

Support using S3 presigned URLs for archive downloads. Requires:

- Adding ``DEVILRY_USE_STORAGE_BACKEND_URL_FOR_ARCHIVE_DOWNLOADS = True`` to settings.
- Using the ``storages.backends.s3.S3Storage`` storage backend.


Update devilry to 3.6.5
##############################

Update the devilry version to ``3.3.5`` as described in :doc:`../update`.
