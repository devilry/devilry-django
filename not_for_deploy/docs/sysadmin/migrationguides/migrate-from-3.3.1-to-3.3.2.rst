=============================
Migrating from 3.3.1 to 3.3.2
=============================

.. note::
    This is a beta release.

Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


Whats new
#########

- Generate ZIP archive for admins.
- Upcoming assignment within the next 7 days added to student dashboard.
- Fixed comment activity filtering.


Update devilry to 3.3.2
#######################

Update the devilry version to ``3.3.2`` as described in :doc:`../update`.

After updating, you need to run::

    $ venv/bin/python manage.py devilry_delete_compressed_archives --all
