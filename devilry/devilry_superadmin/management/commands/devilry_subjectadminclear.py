from django.core.management.base import CommandError

from devilry.devilry_superadmin.management.commands.devilry_subjectadminadd import AdminAddBase


class Command(AdminAddBase):
    args = '<subject-short_name>'
    help = 'Clear subject admins (removes all subject admins on a subject).'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Subject is required. See --help.')
        short_name = args[0]
        subject = self.get_subject(short_name)
        subject.admins.clear()
