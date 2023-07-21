===========================
Migrating from 5.x to 6.0.0
===========================

.. note::
    Migrate from the latest 5.x release to 6.0.0.


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########
 - Updated Devilry to Django 4.2
 - Python 3.10 support
 - Add health-check endpoints.
   - `_api/application-state/ready`. Use this for initial ready-check. It's not recommended to use this too often as it performs a database-query (use the `live`-endpoint for that).
   - `_api/application-state/alive`. Use this if you need to continously check if the application is up and running. Just a simple request, no database-query performed.
 - Group invitations: Now using the devilry_message backend for storing messages.


Fixed
#####
- WCAG: Contrast-issue with link in "No access" warning-box.
- Translations: Various translation errors.
- Self-assign: Issue with duplicate rows from query when examiner is self-assigning.
- Self-assign: Missing CSRF-token.
- Comment-notification to examiners: When examiner posts comments all admins are notified.



Update devilry to 6.0.0
#######################

Update the devilry version to ``6.0.0`` as described in :doc:`../update`.
