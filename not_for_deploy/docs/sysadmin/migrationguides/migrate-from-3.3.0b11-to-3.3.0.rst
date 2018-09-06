================================
Migrating from 3.3.0b11 to 3.3.0
================================

.. note::
    This is a beta release.

Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########
- Add missing static files.
- Add fix for passing students based on results from earlier semesters.


Update devilry to 3.3.0
#######################

Update the devilry version to ``3.3.0`` as described in :doc:`../update`.

After updating, you need to run::

    $ venv/bin/python manage.py devilry_delete_compressed_archives --all
