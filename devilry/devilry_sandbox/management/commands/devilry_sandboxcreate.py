from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from devilry.devilry_sandbox.sandbox import Sandbox


class Command(BaseCommand):
    help = 'Sandbox setup script.'

    option_list = BaseCommand.option_list + (
        make_option('-s', '--subject-short',
            dest='subject_shortname',
            help='Short name of subject.'),
        make_option('-l', '--subject-long',
            dest='subject_longname',
            help='Long name of subject.'),
        make_option('--subjectadmin', action='store_true',
            default=False, dest='subjectadmin',
            help='Make the test-user subjectadmin. If this is not supplied, the user will be periodadmin.')
    )

    def handle(self, *args, **options):
        with transaction.commit_on_success():
            sandbox = Sandbox()
            test = sandbox.create_user('test', 'Test User')

            subject = sandbox.create_subject(short_name=options['subject_shortname'],
                                             long_name=options['subject_longname'])

            period = sandbox.create_period(subject, short_name='fall2012',
                                           long_name='Fall 2012')

            if options['subjectadmin']:
                subject.admins.add(test)
            else:
                period.admins.add(test)
