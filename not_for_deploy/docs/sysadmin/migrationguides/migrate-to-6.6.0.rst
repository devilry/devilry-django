==================
Migrating to 6.6.0
==================

.. warning:: Always update one version at a time. Do not skip versions unless it is explicitly stated in the migration guide.


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########

- Processing of exam qualification moved to a background task
- Fixed missing counters in period admin views
- Better handling of filter input errors
- Make uploaded files in admin UI searchable
- Support for django-allauth 65+
- Markdown version security update


New management command
######################

When moving the exam qualification processing to a background-task, we also moved away from storing the 
results in session and have now introduced new models to store the processed data (`DraftStatus`).

Set up a cron-tab or similar to run the management command `delete_old_draft_statuses`. The command will default 
to deleting `DraftStatus` objects older than 1 hour, but this can be adjusted with `--hours-old` argument.

Note that there's no reason to keep these entries for extended periods of time, as they are only used to store the 
draft-results of the background processing of exam qualifications. The permanent data is stored in the another model 
when the user chooses to save the drafts.


Update devilry
##############

Update the devilry version to ``6.6.0`` as described in :doc:`../update`.
