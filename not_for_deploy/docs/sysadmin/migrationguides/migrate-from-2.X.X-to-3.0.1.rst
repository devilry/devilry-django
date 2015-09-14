=============================
Migrating from 2.X.X to 3.0.1
=============================

.. warning::

    Devilry 3.0 is not released yet. This guide is a work in progress.


Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry
##############
TODO


Migrate the database
####################

::

    $ python manage.py migrate --fake-initial contenttypes && python manage.py migrate --fake core && python manage.py migrate --fake devilry_gradingsystem 0001 && python manage.py migrate --fake-initial
