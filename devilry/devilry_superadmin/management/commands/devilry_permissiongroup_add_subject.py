from django.core.management.base import BaseCommand, CommandError
from django.db import models

from devilry.apps.core.models import Subject
from devilry.devilry_account.models import PermissionGroup, SubjectPermissionGroup


class Command(BaseCommand):
    help = 'Add subject to a permission group.'

    def add_arguments(self, parser):
        parser.add_argument(
            'short_name',
            help='Short name for the subject. (Required)'),
        parser.add_argument(
            'group_name',
            help='Name of the permission group. (Required)')

    def __get_permission_group(self, group_name):
        try:
            return PermissionGroup.objects\
                .filter(
                    models.Q(grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
                    |
                    models.Q(grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN))\
                .get(name=group_name)
        except PermissionGroup.DoesNotExist:
            raise CommandError('PermissionGroup "{}" does not exist.'.format(group_name))

    def handle(self, *args, **options):
        short_name = options['short_name']
        group_name = options.get('group_name', None)

        try:
            subject = Subject.objects.get(short_name=short_name)
        except Subject.DoesNotExist:
            raise CommandError('Subject with short name "{}" does not exist.'.format(short_name))

        if SubjectPermissionGroup.objects.filter(permissiongroup__name=group_name, subject_id=subject.id):
            raise CommandError('Subject already added to permission group "{}".'.format(group_name))

        permission_group = self.__get_permission_group(group_name=group_name)
        subject_permission_group = SubjectPermissionGroup(
            subject=subject, permissiongroup=permission_group)
        subject_permission_group.full_clean()
        subject_permission_group.save()
