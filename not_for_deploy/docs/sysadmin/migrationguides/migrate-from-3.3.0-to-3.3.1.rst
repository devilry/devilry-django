=============================
Migrating from 3.3.0 to 3.3.1
=============================

.. note::
    This is a beta release.

Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


Patch
#####

- Make ZIP archive names unique for assignment and user.



Update devilry to 3.3.1
#######################

Update the devilry version to ``3.3.1`` as described in :doc:`../update`.

After updating, you need to run::

    $ venv/bin/python manage.py devilry_delete_compressed_archives --all
