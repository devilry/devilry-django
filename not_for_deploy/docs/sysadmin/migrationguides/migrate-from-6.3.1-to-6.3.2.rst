=============================
Migrating from 6.3.1 to 6.3.2
=============================


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.



What's new?
###########
- Removed old delivery models which has not been in use for a long time.
- Remove old gradingsystem plugin apps that are no longer in use, and have not been used for a long time.
- Dependency cleanup and updates.
    - ``dj-static`` has been replaced by ``whitenoise``.
    - RQ and related dependencies has been updated to newer versions that are redis 5+ compatible.
- Various fixes related to using blob storage and memory usage, including settings cleanup,
  blob storage based zip file creation with stable memory usage.
- Separate optional dependencies specifier for prod (see requirements.txt changes section below).


Settings changes
################

Removed settings
================
- ``DEVILRY_FSHIERDELIVERYSTORE_ROOT``
-

Changed settings
================

MIDDLEWARE:
-----------
The ``MIDDLEWARE`` setting now includes:
    - ``whitenoise.middleware.WhiteNoiseMiddleware``
    - ``django.middleware.security.SecurityMiddleware``


STORAGES and related settings
-----------------------------

TODO: storage stuff

DATABASES:
----------
We have changed the postgres database binding from psycopg2 to ``psycopg``. This requires
the following change to the ``ENGINE`` option within the ``DATABASES`` setting::

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            # ...
        }
    }


requirements.txt changes
########################
You need to change:
```
devilry==VERSION
```
to
```
devilry[prod]==VERSION
```
in your ``requirements.txt``.


Update devilry to 6.3.2
#######################

Update the devilry version to ``6.3.2`` as described in :doc:`../update`.
