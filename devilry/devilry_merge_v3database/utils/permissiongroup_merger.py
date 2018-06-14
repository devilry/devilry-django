# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import model_to_dict

from devilry.devilry_merge_v3database.utils import merger
from devilry.devilry_account import models as account_models
from django.conf import settings
from django.contrib.auth import get_user_model


class PermissionGroupMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_account.models.PermissionGroup` from database to
    current default database.
    """
    model = account_models.PermissionGroup

    def update_after_save(self, from_db_object):
        created_datetime = from_db_object.created_datetime
        updated_datetime = from_db_object.updated_datetime
        syncsystem_update_datetime = from_db_object.syncsystem_update_datetime
        account_models.PermissionGroup.objects.filter(name=from_db_object.name).update(
            created_datetime=created_datetime,
            updated_datetime=updated_datetime,
            syncsystem_update_datetime=syncsystem_update_datetime
        )

    def start_migration(self, from_db_object):
        permissiongroup_kwargs = model_to_dict(from_db_object, exclude=['id', 'pk', 'users'])
        permissiongroup = account_models.PermissionGroup(**permissiongroup_kwargs)
        self.save_object(obj=permissiongroup)


class PermissionGroupUserMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_account.models.PermissionGroupUser` from database to
    current default database.
    """
    model = account_models.PermissionGroupUser

    def select_related_foreign_keys(self):
        return ['user', 'permissiongroup']

    def start_migration(self, from_db_object):
        permissiongroup = self.get_permissiongroup_by_name(name=from_db_object.permissiongroup.name)
        user = self.get_user_by_shortname(shortname=from_db_object.user.shortname)
        if permissiongroup and user:
            permissiongroup_user = account_models.PermissionGroupUser(
                permissiongroup_id=permissiongroup.id,
                user_id=user.id)
            self.save_object(obj=permissiongroup_user)
        else:
            raise ValueError('PermissionGroups and Users must be imported before PermissionGroupUser')

