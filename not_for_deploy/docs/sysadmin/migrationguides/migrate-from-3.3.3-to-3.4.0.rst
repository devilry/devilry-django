=============================
Migrating from 3.3.3 to 3.4.0
=============================


Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


Bug fixes and tweaks
####################
 - Only department admins can bulk import students and examiners. This is not exactly a bug fix, but a temporary
 restriction.
 - Examiner name is shown when publishing a grade.
 - Empty comments (comments with files only) are not counted as "comments".
 - Breadcrumb shows the full path in the feedback feed.
 - Add big integer field for compressed archives file size.


Update devilry to 3.4.0
#######################

Update the devilry version to ``3.4.0`` as described in :doc:`../update`.

After updating, you need to run::

    $ venv/bin/python manage.py ievvtasks_customsql -i -r
    $ venv/bin/python manage.py devilry_delete_compressed_archives --all
