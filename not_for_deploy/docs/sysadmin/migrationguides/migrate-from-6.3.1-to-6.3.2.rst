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
- Separate optional dependencies specifier for s3 storage (see requirements.txt changes section below).
- First class S3 compatible storage support with setup examples and local development environment.
- Various fixes related to using blob storage and memory usage, including settings cleanup,
  blob storage based zip file creation with stable memory usage.
- Switch from ZIP to ``.tar.gz`` format for feedbackset downloads.


Settings changes
################

Removed settings
================
- ``DEVILRY_FSHIERDELIVERYSTORE_ROOT``
- ``DEVILRY_DELIVERY_STORE_BACKEND``
- ``DEVILRY_FSHIERDELIVERYSTORE_INTERVAL``

Changed settings
================

MIDDLEWARE:
-----------
The ``MIDDLEWARE`` setting now includes:

- ``whitenoise.middleware.WhiteNoiseMiddleware``
- ``django.middleware.security.SecurityMiddleware``

If you have added them in your own settings file, remove them.


Remove from INSTALLED_APPS (if you have them):
----------------------------------------------
- ``devilry.devilry_import_v2database``
- ``devilry.devilry_gradingsystem``
- ``devilry.devilry_gradingsystemplugin_points``
- ``devilry.devilry_gradingsystemplugin_approved``


STORAGES and related settings
-----------------------------

You need to adjust storages settings - the defaults have changed to make devilry
more blob storage friendly out of the box. You need to look over and adjust these
settings:

- ``DELIVERY_STORAGE_BACKEND``
- ``DELIVERY_TEMPORARY_STORAGE_BACKEND``
- ``CRADMIN_LEGACY_TEMPORARY_FILE_STORAGE_BACKEND``
- ``DEVILRY_COMPRESSED_ARCHIVES_DIRECTORY``
- ``STORAGES``

Look at :doc:`../gettingstarted` for example config, including working S3
configuration with required S3 settings.


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
devilry[s3storage]==VERSION
```
in your ``requirements.txt`` IF you want to use s3 compatible storage. This will
add S3 storage dependencies locked to known working versions (django-storages and boto3)


Update devilry to 6.3.2
#######################

Update the devilry version to ``6.3.2`` as described in :doc:`../update`.
