import arrow
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from devilry.apps.core.models import Period
from devilry.devilry_superadmin.delete_periods.period_delete import PeriodDelete


class Command(BaseCommand):
    """
    Management script for deleting all periods started before a given date.
    """
    args = '<num-months>'
    help = 'Delete semesters and it\'s underlying data with end time older than specified <num-months>. ' \
           'This will delete assignments and all deliveries.' \
           'Will also delete subjects if all semesters for that subject is ' \
           'deleted, but skips initially empty subjects.'

    def add_arguments(self, parser):
        parser.add_argument(
            'num-months',
            help='Integer. Delete semesters that ended before specified months ago.'
        )

    def __confirm_delete(self):
        confirm_string = 'DELETE SEMESTERS'
        input_string = raw_input('Are you sure you want to delete these semesters? '
                                 'All underlying data will also be deleted\n'
                                 'To confirm, type "{}", to exit type "q": '.format(confirm_string))
        if input_string == confirm_string:
            return
        else:
            self.stderr.write('ABORTING... No semesters deleted.')
            raise SystemExit()

    def get_datetime_from_months_ago(self, months_ago):
        return arrow.now().replace(months=-months_ago).datetime

    def handle(self, *args, **options):
        months_ago = int(options['num-months'])
        delete_older_than_datetime = self.get_datetime_from_months_ago(months_ago=months_ago)
        if not Period.objects.filter(end_time__lt=delete_older_than_datetime).exists():
            self.stderr.write('EXITING... There are no semesters that ended before {}.'.format(
                delete_older_than_datetime.strftime('%Y-%m-%d %H:%M')))
            raise SystemExit()

        period_deleter = PeriodDelete(end_time_older_than_datetime=delete_older_than_datetime, log_info=True)

        self.stdout.write('All semesters that ended before {} will be deleted. If all semesters for a subject are '
                          'deleted, the subject will be deleted as well. Preview is shown below:\n'.format(
            delete_older_than_datetime.strftime('%Y-%m-%d %H:%M')))
        self.stdout.write(period_deleter.get_preview())
        self.stdout.write('\n')

        # User must confirm the deletion.
        self.__confirm_delete()

        # Start deletion
        with transaction.atomic():
            call_command('ievvtasks_customsql', '--clear')

            self.stdout.write('Deleting periods...')
            period_deleter.delete()

            call_command('ievvtasks_customsql', '-i', '-r')
