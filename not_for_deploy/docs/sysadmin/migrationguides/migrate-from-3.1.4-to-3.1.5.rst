=============================
Migrating from 3.1.4 to 3.1.5
=============================

Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 3.1.5
#######################

Update the devilry version to ``3.1.5`` as described in :doc:`../update`.

After updating, you need to run::

    $ venv/bin/python manage.py devilry_delete_compressed_archives --all
