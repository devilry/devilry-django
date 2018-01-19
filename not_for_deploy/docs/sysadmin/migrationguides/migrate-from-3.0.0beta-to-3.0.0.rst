=================================
Migrating from 3.0.0beta to 3.0.0
=================================

Backup database and files
#########################
BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 3.0.0
#######################

Update the devilry version to ``3.0.0`` as described in :doc:`../update`, but **do not restart supervisord**.


Migrate the database
####################

::

    $ cd ~/devilrydeploy/
    $ venv/bin/python manage.py migrate


Setup RQ
########
We have replaced Celery with RQ. This means you need to setup RQ
as explained in :doc:`rq`.

If you used djcelery-email as email backend previously,
you will want to update to the new RQ email backend as
explained in :doc:`rq_email`.


Add your own branding
#####################
Simple branding was added in 3.0.0. See :doc:`branding`.
