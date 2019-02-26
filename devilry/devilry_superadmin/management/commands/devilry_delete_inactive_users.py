# -*- coding: utf-8 -*-


import arrow
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction, models
from django.utils import timezone

from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.utils import datetimeutils


class InactiveUserDeleter(object):
    def __init__(self, inactive_since_datetime):
        self.inactive_since_datetime = inactive_since_datetime

    def get_users_to_delete_queryset(self):
        now = timezone.now()

        user_ids = PeriodPermissionGroup.objects\
            .filter(period__start_time__lte=now, period__end_time__gte=now)\
            .values_list('permissiongroup__permissiongroupuser__user_id', flat=True)

        return get_user_model().objects\
            .exclude(
                models.Q(relatedstudent__period__start_time__lte=now,
                         relatedstudent__period__end_time__gte=now)
                |
                models.Q(relatedexaminer__period__start_time__lte=now,
                         relatedexaminer__period__end_time__gte=now))\
            .exclude(is_superuser=True)\
            .exclude(id__in=user_ids)\
            .filter(last_login__lt=self.inactive_since_datetime)

    def delete(self):
        self.get_users_to_delete_queryset().delete()


class Command(BaseCommand):
    """
    Management script for deleting all inactive users.
    """
    help = 'Delete users that hasn\'t logged in since the provided date, or never logged in.' \
           'These users will be excluded from deletion: ' \
           '- Superusers ' \
           '- Students and examiners on active semesters ' \
           '- Period admins on active semesters'

    def add_arguments(self, parser):
        parser.add_argument(
            'inactive_since_datetime',
            type=str,
            help='An ISO formatted datetime string. Example: YYYY-MM-DD HH:mm'
        )

    def __confirm_delete(self):
        confirm_string = 'DELETE USERS'
        self.stdout.write(self.style.ERROR('Are you sure you want to delete these users? This operation can NOT BE UNDONE!'))
        input_string = input('To confirm, type "{}", to exit type "q": '.format(confirm_string))
        if input_string == confirm_string:
            return
        else:
            self.stdout.write(self.style.ERROR('ABORTING... No users deleted.'))
            raise SystemExit()

    def __get_string_formatted_datetime(self, datetime_obj):
        return datetimeutils.isoformat_withseconds(datetime_obj)

    def __preview(self, user_deleter):
        for user in user_deleter.get_users_to_delete_queryset():
            last_login = None
            if user.last_login:
                last_login = arrow.get(
                    user.last_login.astimezone(timezone.get_current_timezone())).format('MMM D. YYYY HH:mm')
            self.stdout.write('- {}: {}\n\tLast login: {}\n\n'.format(
                user.shortname,
                user.get_full_name(),
                last_login))

    def handle(self, *args, **options):
        inactive_since_datetime = datetimeutils.from_isoformat(
            options['inactive_since_datetime']).replace(second=0, microsecond=0)

        # Inactive since must be earlier than now
        now = timezone.now()
        if inactive_since_datetime >= now:
            self.stderr.write(
                'EXITING... Given datetime ({}) must be earlier than now ({})'.format(
                    arrow.get(inactive_since_datetime.astimezone(
                        timezone.get_current_timezone())).format('MMM D. YYYY HH:mm'),
                    arrow.get(now.astimezone(timezone.get_current_timezone())).format('MMM D. YYYY HH:mm')
                ))
            raise SystemExit()

        # Instantiate the user deleter.
        user_deleter = InactiveUserDeleter(inactive_since_datetime=inactive_since_datetime)

        # Check if users exist.
        if not user_deleter.get_users_to_delete_queryset().exists():
            self.stdout.write(self.style.ERROR('EXITING... There are no users with last login before {}.'.format(
                arrow.get(inactive_since_datetime).format('MMM D. YYYY HH:mm'))))
            raise SystemExit()

        self.stdout.write('############################################################\n'
                          '# Delete all users with last login before: {}'
                          '\n############################################################'.format(
            arrow.get(inactive_since_datetime).format('MMM D. YYYY HH:mm')
        ))
        self.stdout.write('\n')

        # Confirm show preview of users to be deleted
        self.stdout.write('Preview of all users that will be deleted:\n\n')
        self.__preview(user_deleter=user_deleter)

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
