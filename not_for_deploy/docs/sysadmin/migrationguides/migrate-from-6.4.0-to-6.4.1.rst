=============================
Migrating from 6.4.0 to 6.4.1
=============================


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########

- Changes to how emails are sent in background tasks. Previously we recommended using RQ email backend to send all
  emails asynchronously. From 6.4.1, we have moved this to a higher level so the old ``DEVILRY_LOWLEVEL_EMAIL_BACKEND``
  has been removed, and we only use the ``EMAIL_BACKEND`` setting.


Update devilry to 6.4.1
#######################

Update the devilry version to ``6.4.1`` as described in :doc:`../update`.

Make sure to make the following changes to settings:

- ``EMAIL_BACKEND``: Set this to the value you currently have in ``DEVILRY_LOWLEVEL_EMAIL_BACKEND``. Example:
  ``EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'``.
- ``DEVILRY_LOWLEVEL_EMAIL_BACKEND``: Remove this setting.

