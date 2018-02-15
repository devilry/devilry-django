=============================
Migrating from 3.0.3 to 3.1.0
=============================

Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 3.1.0
#######################

Update the devilry version to ``3.1.0`` as described in :doc:`../update`.


After update, you have to run
#############################

::

    $ venv/bin/python manage.py ievvtasks_customsql -i -r


Fix your tag-prefixes
#####################
You can change the default tag prefix used with ``devilry_periodsetrelatedexaminers``
and ``devilry_periodsetrelatedstudents`` with the ``DEVILRY_IMPORTED_PERIOD_TAG_DEFAULT_PREFIX``
setting (see :ref:`devilry_settings`).

If you change the ``DEVILRY_IMPORTED_PERIOD_TAG_DEFAULT_PREFIX``, you will want to
update the existing tags to use this new prefix. To do that, we now provide::

    $ venv/bin/python manage.py devilry_rename_periodtag_prefix <old prefix> <new prefix>

The default value for ``DEVILRY_IMPORTED_PERIOD_TAG_DEFAULT_PREFIX`` is ``x``, so lets
say you add the setting for the first time now as::

    DEVILRY_IMPORTED_PERIOD_TAG_DEFAULT_PREFIX = 'fs'

You will then need to run::

    $ venv/bin/python manage.py devilry_rename_periodtag_prefix x fs
