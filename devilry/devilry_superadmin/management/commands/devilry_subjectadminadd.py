from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class AdminAddBase(BaseCommand):
    def add_admin(self, record, username):
        try:
            user = get_user_model().objects.get(shortname=username)
        except get_user_model().DoesNotExist, e:
            raise CommandError('Invalid username.')

        if record.admins.filter(username=username).count() > 0:
            raise CommandError('User is already admin on this subject.')
        else:
            record.admins.add(user)

    def get_subject(self, short_name):
        from devilry.apps.core.models import Subject
        try:
            return Subject.objects.get(short_name=short_name)
        except Subject.DoesNotExist, e:
            raise CommandError('Invalid subject-short_name.')


class Command(AdminAddBase):
    args = '<subject-short_name> <admin-username>'
    help = 'Add subject admin.'

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('Subject and admin-username is required. See --help.')
        short_name = args[0]
        username = args[1]
        subject = self.get_subject(short_name)
        self.add_admin(subject, username)
