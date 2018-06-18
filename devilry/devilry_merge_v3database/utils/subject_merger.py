# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import model_to_dict

from devilry.devilry_merge_v3database.utils import merger
from devilry.devilry_account import models as account_models
from devilry.apps.core import models as core_models


class SubjectMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.apps.core.models.Subject` from database to
    current default database.
    """
    model = core_models.Subject

    def update_after_save(self, from_db_object):
        core_models.Subject.objects\
            .filter(short_name=from_db_object.short_name)\
            .update(etag=from_db_object.etag)

    def start_migration(self, from_db_object):
        if not core_models.Subject.objects.filter(short_name=from_db_object.short_name).exists():
            subject_kwargs = model_to_dict(from_db_object, exclude=['id', 'pk', 'admins'])
            subject = core_models.Subject(**subject_kwargs)
            self.save_object(obj=subject)


class SubjectPermissionGroupMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_account.models.SubjectPermissionGroup` from database to
    current default database.
    """
    model = account_models.SubjectPermissionGroup

    def select_related_foreign_keys(self):
        return ['subject', 'permissiongroup']

    def start_migration(self, from_db_object):
        subject = self.get_subject_by_shortname(shortname=from_db_object.subject.short_name)
        permission_group = self.get_permissiongroup_by_name(name=from_db_object.permissiongroup.name)
        if subject and permission_group:
            subject_permissiongroup = account_models.SubjectPermissionGroup(
                permissiongroup_id=permission_group.id,
                subject_id=subject.id
            )
            self.save_object(obj=subject_permissiongroup)
        else:
            raise ValueError('Subjects and PermissionGroups must be imported before SubjectPermissionGroups')

