import pprint

from django.contrib.auth import get_user_model

from devilry.apps.core.models import Subject
from devilry.devilry_account import models as account_models
from devilry.devilry_import_v2database import modelimporter


class NodeImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return None

    def _bulk_create_subject_permission_groups(self, permission_group, subject_queryset):
        """
        Bulk-creates ``SubjectPermissionGroup``s for the all the ``Subject``s under this ``Node``.

        Args:
            permission_group: The department-admin ``PermissionGroup``.
            subject_queryset: QuerySet of ``Subject``s.
        """
        subject_permission_group_list = []
        for subject in subject_queryset:
            subject_permission_group_list.append(
                account_models.SubjectPermissionGroup(
                    subject=subject,
                    permissiongroup=permission_group)
            )
        account_models.SubjectPermissionGroup.objects.bulk_create(subject_permission_group_list)

    def _bulk_create_permission_group_users(self, permission_group, admin_user_queryset):
        """
        Bulk-creates ``PermissionGroupUser``s for the ``PermissionGroup``.

        Args:
            permission_group: The department-admin ``PermissionGroup``.
            admin_user_queryset: QuerySet of ``User``s.
        """
        permission_group_user_list = []
        for user in admin_user_queryset:
            permission_group_user_list.append(
                account_models.PermissionGroupUser(
                    permissiongroup=permission_group,
                    user=user
                )
            )
        account_models.PermissionGroupUser.objects.bulk_create(permission_group_user_list)

    def _create_permission_groups_for_admins(self, name, subject_queryset, admin_user_queryset):
        """
        Create a ``PermissionGroup`` with ``SubjectPermissionGroup``s for each ``Subject`` that is directly or
        indirectly a child of this ``Node``. Also creates ``PermissionGroupUser``s for each user that was assigned as
        an admin for this ``Node``.

        NOTE::
            We do not create a ``Node`` as this is not used in Devilry 3.0. Administrators for ``Node``s are
            department admins in 3.0.

        Args:
            name: Name of the ``PermissionGroup``. Must be unique.
            subject_queryset: QuerySet of ``Subject``s.
            admin_user_queryset: QuerySet of ``User``s that will be set as department-admins.
        """
        permission_group = account_models.PermissionGroup(
            name=name,
            grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN
        )
        permission_group.full_clean()
        permission_group.save()
        self._bulk_create_subject_permission_groups(permission_group, subject_queryset)
        self._bulk_create_permission_group_users(permission_group, admin_user_queryset)

    def _get_user_queryset(self, admin_user_ids_list):
        return get_user_model().objects.filter(id__in=admin_user_ids_list)

    def _get_subject_queryset(self, subject_ids_list):
        return Subject.objects.filter(id__in=subject_ids_list)

    def _create_node_permissions_from_object_dict(self, object_dict):
        subject_queryset = self._get_subject_queryset(object_dict['subject_ids'])
        admin_user_queryset = self._get_user_queryset(object_dict['admin_user_ids'])
        self._create_permission_groups_for_admins(
            name=object_dict['fields']['short_name'],
            subject_queryset=subject_queryset,
            admin_user_queryset=admin_user_queryset
        )

    def import_models(self, fake=False):
        for object_dict in self.v2node_directoryparser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_node_permissions_from_object_dict(object_dict=object_dict)
