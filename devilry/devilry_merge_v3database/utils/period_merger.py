# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import model_to_dict

from devilry.devilry_merge_v3database.utils import merger
from devilry.devilry_account import models as account_models
from devilry.apps.core import models as core_models


class PeriodMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.apps.core.models.Period` from database to
    current default database.
    """
    model = core_models.Period

    def select_related_foreign_keys(self):
        return ['parentnode']

    def update_after_save(self, from_db_object):
        core_models.Period.objects\
            .filter(short_name=from_db_object.short_name, parentnode__short_name=from_db_object.parentnode.short_name)\
            .update(etag=from_db_object.etag)

    def start_migration(self, from_db_object):
        subject = self.get_subject_by_shortname(shortname=from_db_object.parentnode.short_name)
        if subject:
            period_kwargs = model_to_dict(from_db_object, exclude=['id', 'pk', 'parentnode', 'admins'])
            period = core_models.Period(**period_kwargs)
            period.parentnode_id = subject.id
            self.save_object(obj=period)
        else:
            raise ValueError('Subjects must be imported before Periods.')


class PeriodPermissionGroupMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_account.models.PeriodPermissionGroup` from database to
    current default database.
    """
    model = account_models.PeriodPermissionGroup

    def select_related_foreign_keys(self):
        return ['period', 'period__parentnode', 'permissiongroup']

    def start_migration(self, from_db_object):
        period = self.get_period_by_shortname(
            shortname=from_db_object.period.short_name,
            parentnode_shortname=from_db_object.period.parentnode.short_name)
        permission_group = self.get_permissiongroup_by_name(name=from_db_object.permissiongroup.name)
        if period and permission_group:
            period_permissiongroup = account_models.PeriodPermissionGroup(
                permissiongroup_id=permission_group.id,
                period_id=period.id
            )
            self.save_object(obj=period_permissiongroup)
        else:
            raise ValueError('Periods and PermissionGroups must be imported before PeriodPermissionGroups')


class PeriodTagMerger(merger.AbstractMerger):
    """
    TODO: Finish after RelatedStudent and RelatedExaminer mergers are complete.

    Merge :class:`devilry.apps.core.models.PeriodTag` from database to
    current default database.
    """
    model = core_models.PeriodTag

    def select_related_foreign_keys(self):
        return ['period']

    def start_migration(self, from_db_object):
        pass
