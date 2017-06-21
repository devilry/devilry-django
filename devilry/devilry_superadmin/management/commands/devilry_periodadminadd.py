from django.core.management.base import CommandError

from devilry.apps.core.models import Period
from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_superadmin.management.commands.devilry_subjectadminadd import AdminAddBase


class Command(AdminAddBase):
    help = 'Add period admin.'

    @property
    def permissiongroup_type(self):
        return PermissionGroup.GROUPTYPE_PERIODADMIN

    def add_arguments(self, parser):
        parser.add_argument(
            'subject_short_name',
            help='Short name of the subject that contains the period you '
                 'wish to add an admin to.')
        parser.add_argument(
            'period_short_name',
            help='Short name of the period you wish to add an admin to.')
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        subject_short_name = options['subject_short_name']
        period_short_name = options['period_short_name']
        subject = self.get_subject(subject_short_name)
        try:
            period = Period.objects.get(short_name=period_short_name, parentnode=subject)
        except Period.DoesNotExist, e:
            raise CommandError('Invalid period_short_name.')

        self.basenode = period
        super(Command, self).handle(*args, **options)
