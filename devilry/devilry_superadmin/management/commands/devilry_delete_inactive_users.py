from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from devilry.utils import datetimeutils


class DeleteInactiveUsers(object):
    def __init__(self, inactive_since_datetime):
        self.inactive_since_datetime = inactive_since_datetime

    def get_users_to_delete_queryset(self):
        return get_user_model().objects\
            .exclude(is_superuser=True)\
            .filter(last_login__lt=self.inactive_since_datetime)

    def delete(self):
        self.get_users_to_delete_queryset().delete()


class Command(BaseCommand):
    """
    Management script for deleting all inactive users.
    """
    help = 'Delete users that hasn\'t logged in since the provided date. Superusers are excluded, ' \
           'and needs to be deleted manually.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--inactive-since-datetime',
            type=str,
            required=True,
            help='An ISO formatted datetime string. Example: YYYY-MM-DD HH:mm:ss'
        )

    def __confirm_delete(self):
        confirm_string = 'DELETE USERS'
        input_string = raw_input('Are you sure you want to delete these users?\n'
                                 'To confirm, type "{}", to exit type "q": '.format(confirm_string))
        if input_string == confirm_string:
            return
        else:
            self.stderr.write('ABORTING... No users deleted.')
            raise SystemExit()

    def __get_string_formatted_datetime(self, datetime_obj):
        return datetimeutils.isoformat_withseconds(datetime_obj)

    def __confirm_preview(self, user_deleter):
        input_string = raw_input('\n\nDo you want a preview of the users to delete?\n'
                                 'Type "y" to show preview, or type "n" to skip: ')
        if input_string == 'y':
            for user in user_deleter.get_users_to_delete_queryset():
                self.stdout.write('\n')
                self.stdout.write('\t- {}: {}\n\t\tLast login: {}\n\n'.format(
                    user.shortname, user.get_full_name(), datetimeutils.isoformat_withseconds(user.last_login)))
        else:
            return

    def handle(self, *args, **options):
        inactive_since_datetime = datetimeutils.from_isoformat(options['inactive_since_datetime'])
        print inactive_since_datetime

        # Check if users exist.
        if not get_user_model().objects.filter(last_login__lt=inactive_since_datetime).exists():
            self.stderr.write('EXITING... There are no users that has not logged in since {}.'.format(
                datetimeutils.isoformat_withseconds(inactive_since_datetime)))
            raise SystemExit()

        # Instantiate the user deleter.
        user_deleter = DeleteInactiveUsers(inactive_since_datetime=inactive_since_datetime)

        self.stdout.write('\n\nAll users that have not logged in since {} will be deleted:\n'.format(
            datetimeutils.isoformat_withseconds(inactive_since_datetime)))

        # Confirm show preview of users to be deleted
        self.__confirm_preview(user_deleter=user_deleter)

        # User must confirm the deletion.
        self.stdout.write('\n\nThis action will delete {} users.'.format(
            user_deleter.get_users_to_delete_queryset().count()))
        self.__confirm_delete()

        # Start deletion
        with transaction.atomic():
            call_command('ievvtasks_customsql', '--clear')

            self.stdout.write('Deleting users...')
            user_deleter.delete()

            call_command('ievvtasks_customsql', '-i', '-r')
