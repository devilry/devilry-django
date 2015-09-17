=============================
Migrating from 2.X.X to 3.0.1
=============================

.. warning::

    Devilry 3.0 is not released yet. This guide is a work in progress.


Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 3.0.0
#######################

Update the devilry version to ``3.0.0`` as described in :doc:`update`, but **do not restart supervisord**.


Migrate the database for 3.0.0
##############################

::

    $ cd ~/devilrydeploy/
    $ venv/bin/python manage.py migrate --fake-initial contenttypes && python manage.py migrate --fake core && python manage.py migrate --fake devilry_gradingsystem 0001 && python manage.py migrate --fake-initial


Update devilry to 3.0.1
#######################

Update the devilry version to ``3.0.1`` as described in :doc:`update`, but **do not restart supervisord**.


Migrate the database for 3.0.1
##############################
::

    $ cd ~/devilrydeploy/
    $ venv/bin/python manage.py migrate --fake-initial --noinput


Add missing permissions
#######################
TODO - must include information about departments administrators
and assignment administrators.
