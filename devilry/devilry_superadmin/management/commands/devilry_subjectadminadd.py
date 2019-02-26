
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from devilry.devilry_account.models import PermissionGroup, PermissionGroupUser


class AdminAddBase(BaseCommand):
    @property
    def _permission_group_name(self):
        return '{prefix}-{path}#<subject_id>'.format(
            prefix=settings.DEVILRY_SYNCSYSTEM_SHORTNAME,
            path=self.basenode.get_path(),
            id=self.basenode.id)

    @property
    def permissiongroup_type(self):
        raise NotImplementedError()

    def add_admin(self):
        try:
            user = get_user_model().objects.get(shortname=self.user_shortname)
        except get_user_model().DoesNotExist:
            raise CommandError('Invalid user_shortname.')

        permissiongroup, created = PermissionGroup.objects.create_or_update_syncsystem_permissiongroup(
            basenode=self.basenode,
            grouptype=self.permissiongroup_type)
        if not permissiongroup.users.filter(id=user.id):
            permissiongroupuser = PermissionGroupUser(
                permissiongroup=permissiongroup,
                user=user)
            permissiongroupuser.full_clean()
            permissiongroupuser.save()
            permissiongroup.syncsystem_update_datetime = timezone.now()
            permissiongroup.save()

    def get_subject(self, short_name):
        from devilry.apps.core.models import Subject
        try:
            return Subject.objects.get(short_name=short_name)
        except Subject.DoesNotExist:
            raise CommandError('Invalid subject_short_name.')

    def add_arguments(self, parser):
        parser.add_argument(
            'user_shortname',
            help='Short name of the user that you wish to add as admin. '
                 'The short name of a user is the username if authenticating '
                 'with username, and email if not.')

    def handle(self, *args, **options):
        self.user_shortname = options['user_shortname']
        self.add_admin()


class Command(AdminAddBase):
    help = 'Add a subject admin.'

    @property
    def permissiongroup_type(self):
        return PermissionGroup.GROUPTYPE_SUBJECTADMIN

    def add_arguments(self, parser):
        parser.add_argument(
            'subject_short_name',
            help='Short name of the subject you wish to add an admin to.')
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        subject_short_name = options['subject_short_name']
        self.basenode = self.get_subject(subject_short_name)
        super(Command, self).handle(*args, **options)
