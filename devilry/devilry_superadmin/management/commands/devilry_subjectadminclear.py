from django.core.management.base import CommandError, BaseCommand

from devilry.apps.core.models import Subject, Period
from devilry.devilry_account.models import PermissionGroup


class Command(BaseCommand):
    help = 'Clear subject admins (removes the syncsystem permission group ' \
           'for the subject).'

    def add_arguments(self, parser):
        parser.add_argument(
            'subject_short_name',
            help='Short name of the subject that contains the subject you '
                 'wish to add an admin to.')

    def handle(self, *args, **options):
        subject_short_name = options['subject_short_name']

        try:
            subject = Subject.objects.get(short_name=subject_short_name)
        except Subject.DoesNotExist:
            raise CommandError('Invalid subject_short_name.')

        try:
            permissiongroup = PermissionGroup.objects.get_syncsystem_permissiongroup(
                grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                basenode=subject)
        except PermissionGroup.DoesNotExist:
            self.stdout.write('WARNING: No sync-system permission group exists '
                              'for this subject, so there is no admins to clear.')
            return
        else:
            permissiongroup.delete()
