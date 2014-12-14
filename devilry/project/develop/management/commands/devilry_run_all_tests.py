from django.core import management
from optparse import make_option


tests = [
    'devilry',
    'devilry_subjectadmin',
    'devilry_usersearch',
]


class Command(management.base.BaseCommand):
    help = 'Run all our tests'
    option_list = management.base.BaseCommand.option_list + (
        make_option(
            '--failfast',
            action='store_true',
            dest='failfast',
            default=False,
            help='Tells Django to stop running the test suite after first '
                 'failed test.'),
    )

    def handle(self, *args, **options):
        management.call_command(
            'test', *tests,
            verbosity=options['verbosity'],
            failfast=options['failfast'],
            traceback=options['traceback'])
