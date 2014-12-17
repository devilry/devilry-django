from django.core.management.base import CommandError

from devilry.devilry_superadmin.management.commands.devilry_subjectadminadd import AdminAddBase



class Command(AdminAddBase):
    args = '<subject-short_name> <period-short-name> <admin-username>'
    help = 'Add period admin.'

    def handle(self, *args, **options):
        from devilry.apps.core.models import Period

        if len(args) != 3:
            raise CommandError('Subject, Period and admin-username is required. See --help.')
        subject_short_name = args[0]
        period_short_name = args[1]
        username = args[2]

        subject = self.get_subject(subject_short_name)
        try:
            period = Period.objects.get(short_name=period_short_name, parentnode=subject)
        except Period.DoesNotExist, e:
            raise CommandError('Invalid period-short_name.')
        self.add_admin(period, username)
