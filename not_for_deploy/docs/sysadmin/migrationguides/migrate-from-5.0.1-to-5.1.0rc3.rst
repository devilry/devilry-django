================================
Migrating from 5.0.1 to 5.1.0rc3
================================


What's new
##########

- Updated to Django 3.1.*
- Replaced model_mommy model-fixture package with model_bakery
- Add tag-filter option for students/examiners with no PeriodTags
- Examiners can filter students/groups by PeriodTags
- devilry_errortemplates: New app for handling custom error templates


Fixes
#####
- Fixed contrast and aria-issues
- Calender rendering issue for Safari on iPad
- Added missing admin-model for GroupInvite
- NullBooleanField: Migrated to BooleanField(null=True, ...). NullBooleanField is deprecated in Django 3, and will be removed in Django 4.
- JSONField: Migration. JSONField is now built-in, and should be imported from django.db.models. django.contrib.postgres.fields.JSONField is deprecated in Django 3, and will be removed in Django 4.
- Removed django_errortemplates as requirement, replaced with django_errortemplates instead.


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


Update devilry to 5.1.0rc3
##########################

Uninstall django_errortemplates with PIP **between** step 2 and 3 in the :doc:`../update`::

    $ cd ~/devilrydeploy
    $ venv/bin/pip uninstall django_errortemplates

Update the devilry version to ``5.1.0rc3`` as described in :doc:`../update`.
