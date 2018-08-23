from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from devilry.devilry_comment.models import Comment
from devilry.utils import anonymize_database


class Command(BaseCommand):
    """
    Management script for anonymizing the database.
    """
    help = 'Anonymize the entire database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fast',
            action='store_true',
            default=False,
            help='Fast mode sets all identifiers such as name, emails, usernames as the IDs of the object. '
                 'Passing this flag as False will generate random characters the same length of the username. '
        )

    def handle(self, *args, **options):
        fast = options['fast']

        with transaction.atomic():
            call_command('ievvtasks_customsql', '--clear')

            self.stdout.write('Anonymizing the database...')
            db_anonymizer = anonymize_database.AnonymizeDatabase(fast=fast)
            self.stdout.write('Anonymizing all users... ({})'.format(get_user_model().objects.count()))
            db_anonymizer.anonymize_user()
            self.stdout.write('Anonymizing all comments and files...({})'.format(Comment.objects.count()))
            db_anonymizer.anonymize_comments()

            self.stdout.write('(Dataporten) Deleting all SocialAccounts ({})'.format(
                SocialAccount.objects.count()))
            SocialAccount.objects.all().delete()
            self.stdout.write('(Dataporten) Deleting all SocialTokens ({})'.format(
                SocialToken.objects.count()))
            SocialToken.objects.all().delete()
            self.stdout.write('(Dataporten) Deleting all SocialApplications ({})'.format(
                SocialApp.objects.count()))
            SocialApp.objects.all().delete()

            call_command('ievvtasks_customsql', '-i', '-r')

            self.stdout.write('Setting all passwords to test')
            call_command('ievvtasks_set_all_passwords_to_test')
