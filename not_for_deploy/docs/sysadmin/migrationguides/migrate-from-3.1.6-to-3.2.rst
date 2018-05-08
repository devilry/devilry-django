===========================
Migrating from 3.1.6 to 3.2
===========================

.. note::
    NOT RELEASED YET

Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 3.2
#####################

Update the devilry version to ``3.2`` as described in :doc:`../update`.


Bug fixes
#########

- Assignment overview statistics fixed.
- Username in comments missing if candidate was removed.
- Navigating between Devilry and Dataporten after login redirected to an error page.
- Deadlines not sorted in deadline management app.



What is new in the feed(everyone)
#################################

- If a grade is edited, a log will now show from-grade and to-grade as events in the feed.
- Info box regarding hard deadlines.



What is new for admins
######################

- Admins can toggle between hard and soft deadlines. Students can not upload files or comment if
  assignment deadline handling is HARD and has expired.
- Added feature to administrator dashboard where admins can now search for students and go directly to their
  delivery feed. Here they can easily access deadline management for that student/group, see deliveries etc.
- Removed unnecessary step to get to a students feedbackfeed.
- Admins can move deadlines and give new attempts directly in the feed(same as examiners).



What is new for sysadmins
#########################

- Can add custom favicon. See :ref:`custom_favicon`.
- Can add customized info texts for the feed when deadline handling is HARD. See :ref:`editable_ui_messages`.

