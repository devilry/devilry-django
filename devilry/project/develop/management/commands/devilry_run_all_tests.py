from django.core import management
from optparse import make_option


tests = [
    'devilry',
    'devilry.devilry_authenticateduserinfo',
    'devilry.devilry_examiner',
    'devilry.devilry_frontpage',
    'devilry.devilry_gradingsystem',
    'devilry.devilry_gradingsystemplugin_approved',
    # 'devilry_gradingsystemplugin_form',
    'devilry.devilry_gradingsystemplugin_points',
    'devilry_header',
    'devilry_i18n',
    'devilry_nodeadmin',
    'devilry_qualifiesforexam',
    'devilry_qualifiesforexam_approved',
    'devilry_qualifiesforexam_points',
    'devilry_qualifiesforexam_select',
    # #'devilry_search', NOT included because it requires a real search engine like solr
    # 'devilry_student',
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
