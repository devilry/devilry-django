======================================
Migrating from 3.0.0 or 3.0.2 to 3.0.3
======================================

Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 3.0.3
#######################

Update the devilry version to ``3.0.3`` as described in :doc:`../update`.


After update, you should run
############################

::

    $ venv/bin/python manage.py ievvtasks_customsql -i -r
    $ venv/bin/python manage.py devilry_fix_missing_first_feedbackset
