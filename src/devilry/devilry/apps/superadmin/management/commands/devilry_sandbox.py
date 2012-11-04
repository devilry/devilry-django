from django.core.management.base import BaseCommand
from django.db import transaction

from optparse import make_option

from devilry.utils.livesandbox import LiveSandbox


class Command(BaseCommand):
    help = 'Sandbox setup script.'

    option_list = BaseCommand.option_list + (
        make_option('--subject-short',
            dest='subject_shortname',
            help='Short name of subject.'),
        make_option('--subject-long',
            dest='subject_longname',
            help='Long name of subject.'),
        make_option('--username',
            dest='username',
            help='Username of the sandbox user.'),
        make_option('--fullname',
            dest='fullname',
            help='Full name of the sandbox user.')
    )

    def handle(self, *args, **options):
        with transaction.commit_on_success():
            sandbox = LiveSandbox(adminusername=options['username'],
                                  adminfullname=options['fullname'])
            subject = sandbox.create_subject(short_name=options['subject_shortname'],
                                             long_name=options['subject_longname'])
            period = sandbox.create_period(subject, short_name='fall2012',
                                           long_name='Fall 2012')
