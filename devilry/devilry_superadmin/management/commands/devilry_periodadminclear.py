from django.core.management.base import CommandError

from devilry.devilry_superadmin.management.commands.devilry_subjectadminadd import AdminAddBase


class Command(AdminAddBase):
    args = '<subject-short_name> <period short name>'
    help = 'Clear period admins (removes all subject admins on a subject).'

    def handle(self, *args, **options):
        from devilry.apps.core.models import Period

        if len(args) != 2:
            raise CommandError('Subject and period is required. See --help.')
        short_name = args[0]
        period_short_name = args[1]

        subject = self.get_subject(short_name)
        try:
            period = Period.objects.get(short_name=period_short_name, parentnode=subject)
        except Period.DoesNotExist, e:
            raise CommandError('Invalid period-short_name.')
        period.admins.clear()
