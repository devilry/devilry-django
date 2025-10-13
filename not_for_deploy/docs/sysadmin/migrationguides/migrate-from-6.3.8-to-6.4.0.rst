=============================
Migrating from 6.3.8 to 6.4.0
=============================

Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########

- DeleteView handling moved to form_valid(). #1293
- Student dashboard now correctly displays Norwegian ordinal numbers (e.g., "4. forsøk"). #1305
- Compatibility issues with boto3/botocore 1.36. #1322
- Notification template mismatch. #1315
- Automated directory naming causing npm issues. #1071
- System message templating issues. #1316
- Corrected file names for presigned URLs of non-Tar files. #1321
- Feedbackfeed raising Http404 for examiners. #1287


Update devilry to 6.4.0
#######################

Update the devilry version to ``6.4.0`` as described in :doc:`../update`.

