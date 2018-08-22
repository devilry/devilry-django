=================================
Migrating from 3.3.0b7 to 3.3.0b8
=================================

.. note::
    This is a beta release

Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


What's new in 3.3.0b8?
######################

- Handle user.shortname for devilry_periodsetrelatedstudents script.
- Fix merged groups representation in feed.


Update devilry to 3.3.0b8
#########################

Update the devilry version to ``3.3.0b7`` as described in :doc:`../update`.

After the update, run::

    $ python manage.py ievvtasks_customsql  -i -r


