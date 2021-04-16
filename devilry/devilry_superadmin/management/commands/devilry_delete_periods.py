# -*- coding: utf-8 -*-


import arrow
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from devilry.apps.core.models import Period
from devilry.devilry_superadmin.delete_periods.period_delete import PeriodDelete
from devilry.utils import datetimeutils


class Command(BaseCommand):
    """
    Management script for deleting all periods ended before a given date.
    """
    args = '<datetime>'
    help = 'Delete semesters and it\'s underlying data with end time older than specified <datetime>. ' \
           'This will delete assignments and all deliveries.' \
           'Will also delete subjects if all semesters for that subject is ' \
           'deleted, but skips initially empty subjects.'

    def add_arguments(self, parser):
        parser.add_argument(
            'datetime',
            type=str,
            help='An ISO formatted datetime string. Example: YYYY-MM-DD HH:mm'
        )
        parser.add_argument(
            '--delete-empty-subjects',
            dest='delete_empty_subjects',
            action='store_true',
            default=False,
            help='If all semesters within a subject are deleted, delete the subject as well.'
        )
        parser.add_argument(
            '--skip-confirm-delete',
            dest='skip_confirm_delete',
            action='store_true',
            default=False,
            help='Skips confirm delete. This is mostly here for the automated tests. In most cases you DO NOT want to skip the confirm message, which will give you summary before the delete operation.'
        )

    def __confirm_delete(self):
        confirm_string = 'DELETE SEMESTERS'
        self.stdout.write('Are you sure you want to delete these semesters and all underlying data?')
        self.stdout.write(
            self.style.ERROR('This operation can NOT BE UNDONE!'))
        input_string = input('To confirm, type "{}", to exit type "q": '.format(confirm_string))
        if input_string == confirm_string:
            return
        else:
            self.stderr.write('ABORTING... No semesters deleted.')
            raise SystemExit()

    def get_datetime_from_months_ago(self, months_ago):
        return arrow.now().replace(months=-months_ago).datetime

    def handle(self, *args, **options):
        delete_older_than_datetime = datetimeutils.from_isoformat(
            options['datetime']).replace(second=0, microsecond=0)
        delete_empty_subjects = options['delete_empty_subjects']
        skip_confirm_delete = options['skip_confirm_delete']

        now = timezone.now()
        if delete_older_than_datetime >= now:
            self.stderr.write(
                'EXITING... Given datetime {} must be earlier than now ({})'.format(
                    arrow.get(delete_older_than_datetime.astimezone(
                        timezone.get_current_timezone())).format('MMM D. YYYY HH:mm'),
                    arrow.get(
                        now.astimezone(timezone.get_current_timezone())).format('MMM D. YYYY HH:mm')
                ))
            raise SystemExit()

        if not Period.objects.filter(end_time__lt=delete_older_than_datetime).exists():
            self.stderr.write(
                'EXITING... There are no semesters that ended before {}.'.format(
                    arrow.get(delete_older_than_datetime).format('MMM D. YYYY HH:mm')))
            raise SystemExit()

        self.stdout.write('###########################################################\n'
                        '# Delete all semesters that ended before: {}\n'
                        '# Delete subjects if all semester are deleted: {}'
                        '\n###########################################################'.format(
            arrow.get(delete_older_than_datetime).format('MMM D. YYYY HH:mm'),
            'YES' if delete_empty_subjects else 'NO'
        ))

        # Instantiate period deleter
        period_deleter = PeriodDelete(
            end_time_older_than_datetime=delete_older_than_datetime,
            delete_empty_subjects=delete_empty_subjects,
            log_info=True)

        self.stdout.write(
            '\nPreview of semesters that will be deleted:\n'.format(
                arrow.get(delete_older_than_datetime).format('MMM D. YYYY HH:mm')))
        self.stdout.write('\n')
        self.stdout.write(period_deleter.get_preview())
        self.stdout.write('\n')

        # User must confirm the deletion.
        if not skip_confirm_delete:
            self.__confirm_delete()

        # Start deletion
        with transaction.atomic():
            call_command('ievvtasks_customsql', '--clear')

            self.stdout.write('Deleting periods...')
            period_deleter.delete()

            call_command('ievvtasks_customsql', '-i', '-r')
