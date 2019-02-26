import fnmatch
import os
import random
from datetime import timedelta
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create deliveries from files found in the given directory.'
    args = '<assignment-path> <directory>'
    option_list = BaseCommand.option_list + (
        make_option(
            '-p', '--patterns',
            default='*.java,*.py,*.txt,*.pdf',
            help=(
                'Comma-separated string of glob patterns to use to search for files in the directory. '
                'The pattern is applied to each file without directory. '
                'Defaults to "*.java,*.py,*.txt,*.pdf,*.rst,*.doc"')),
        make_option(
            '--minfiles',
            type='int',
            default=1,
            help='Minimum number of files per delivery. Defaults to 1.'),
        make_option(
            '--maxfiles',
            type='int',
            default=3,
            help='Maximum number of files per delivery. Defaults to 3.'),
        make_option(
            '--mindeliveries',
            type='int',
            default=0,
            help='Minimum number of deliveries per delivery. Defaults to 0.'),
        make_option(
            '--maxdeliveries',
            type='int',
            default=3,
            help='Maximum number of deliveries per delivery. Defaults to 3.'),
    )

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('This command requires two arguments. See --help.')
        self.assignmentpath = args[0]
        self.directory = args[1]
        self.globpatterns = options['patterns'].split(',')
        self.minfiles = options['minfiles']
        self.maxfiles = options['maxfiles']
        self.mindeliveries = options['mindeliveries']
        self.maxdeliveries = options['maxdeliveries']
        self.verbosity = options['verbosity']
        self._find_assignment()
        self._collect_files()
        self._create_deliveries()

    def _find_assignment(self):
        from devilry.apps.core.models import Assignment
        subject_short_name, period_short_name, assignment_short_name = self.assignmentpath.split('.')
        self.assignment = Assignment.objects.get(
            short_name=assignment_short_name,
            parentnode__short_name=period_short_name,
            parentnode__parentnode__short_name=subject_short_name)

    def _collect_files(self):
        self.files = []
        for root, subdirectories, files in os.walk(self.directory):
            for subdirectory in list(subdirectories):
                if subdirectory.startswith('.'):
                    subdirectories.remove(subdirectory)
            for filename in files:
                if filename.startswith('.'):
                    continue
                for pattern in self.globpatterns:
                    if fnmatch.fnmatch(filename, pattern):
                        self.files.append(os.path.join(root, filename))
        # pprint(self.files)

    def _choose_random_files(self, count):
        chosen_files = set()
        while len(chosen_files) < count:
            filepath = random.choice(self.files)
            if not filepath in chosen_files:
                chosen_files.add(filepath)
        return chosen_files

    def _print_message(self, message):
        if self.verbosity > 0:
            print(message)

    def _create_deliveries(self):
        from devilry.apps.core.models import Delivery

        for assignmentgroup in self.assignment.assignmentgroups.all().prefetch_related('candidates'):
            number_of_deliveries = random.randint(self.mindeliveries, self.maxdeliveries)
            self._print_message('Adding {} deliveries to {}'.format(number_of_deliveries, assignmentgroup))
            try:
                first_canididate = assignmentgroup.candidates.all()[0]
            except IndexError:
                continue
            for deliverynumber in range(number_of_deliveries):
                files = self._choose_random_files(random.randint(self.minfiles, self.maxfiles))
                delivery = Delivery(
                    deadline=assignmentgroup.last_deadline,
                    delivered_by=first_canididate,
                    successful=True,
                    # NOTE: Set time_of_delivery to ensure sorting is correct (can create multiple deliveries during
                    # a single second)
                    time_of_delivery=timezone.now() + timedelta(seconds=deliverynumber))
                delivery.save(autoset_time_of_delivery=False)
                self._print_message('Adding {} files to {}'.format(len(files), delivery))
                for filepath in files:
                    filename = os.path.relpath(filepath, self.directory)
                    delivery.add_file(
                        filename=filename,
                        iterable_data=open(filepath, 'rb')
                    )
