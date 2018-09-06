===================================
Migrating from 3.3.0b10 to 3.3.0b11
===================================

.. note::
    This is a beta release.

Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 3.3.0b11
##########################

Update the devilry version to ``3.3.0b11`` as described in :doc:`../update`.

After updating, you need to run::

    $ venv/bin/python manage.py devilry_delete_compressed_archives --all
