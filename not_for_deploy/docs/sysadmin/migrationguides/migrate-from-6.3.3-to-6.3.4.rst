===========================================
Migrating from 6.3.3 to 6.3.4
===========================================


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########

Add logging for file downloads to enable debugging of issues with downloading large files from S3.
Has to be enabled in settings using::

    LOGGING["loggers"]["devilry.devilry_compressionutil.models"] = {
        'handlers': ['stderr'],
        'level': "DEBUG",
        'propagate': False
    }


Update devilry to 6.3.4
##############################

Update the devilry version to ``6.3.4`` as described in :doc:`../update`.

