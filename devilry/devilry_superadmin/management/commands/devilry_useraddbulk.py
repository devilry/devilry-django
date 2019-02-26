from optparse import make_option
import sys

from django.conf import settings
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand

from devilry.devilry_superadmin.management.commands.devilry_usermod import UserModCommand


class Command(UserModCommand):
    help = 'Add users from standard in or from arguments. Stdin must be a list of ' \
           'usernames or emails separated by whitespace ' \
           '(newline, space or tab).'

    def add_arguments(self, parser):
        parser.add_argument(
            'username_or_email',
            nargs='*',
            help='Usernames or emails. Must be usernames if the '
                 'authentication backend uses usernames, otherwise it must be '
                 'emails.'),

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', '1'))

        if options['username_or_email']:
            usernames = options['username_or_email']
        else:
            if verbosity > 0:
                print("Reading users from stdin...")
            usernames = sys.stdin.read().split()

        users_created_count = 0
        for username in usernames:
            email = None
            if '@' in username:
                email = username
                username = None
            try:
                if username:
                    get_user_model().objects.get_by_username(username=username)
                else:
                    get_user_model().objects.get_by_email(email=email)
            except get_user_model().DoesNotExist:
                get_user_model().objects.create_user(username=username,
                                                     email=email)
                users_created_count += 1
        if verbosity > 0:
            print("Added %d users." % users_created_count)
            print("%s users already existed." % (len(usernames) - users_created_count))
