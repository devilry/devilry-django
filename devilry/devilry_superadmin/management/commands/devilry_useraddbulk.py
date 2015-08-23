from optparse import make_option
import sys
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand

from devilry.devilry_superadmin.management.commands.devilry_usermod import UserModCommand


class Command(UserModCommand):
    help = 'Add users from standard in.'
    option_list = BaseCommand.option_list + (
        make_option('--emailsuffix',
                    dest='emailsuffix',
                    default=None,
                    help='Email suffix set for all users. Example: {username}@example.com'),
    )

    def handle(self, *args, **options):
        print "Reading users from stdin..."
        usernames = sys.stdin.read().split()
        users_created_count = 0
        verbosity = int(options.get('verbosity', '1'))
        emailsuffix = options['emailsuffix']

        for username in usernames:
            try:
                get_user_model().objects.get(shortname=username)
            except get_user_model().DoesNotExist:
                email = None
                if emailsuffix != None:
                    try:
                        email = emailsuffix.format(username=username)
                    except KeyError:
                        print "Error: emailsuffix must contain '{username}'"
                        sys.exit()
                user = get_user_model()(username=username, email=email)
                print "Create user:%s with email %s" % (username, email)
                user.set_unusable_password()
                self.save_user(user, verbosity)
                users_created_count += 1
        if verbosity > 0:
            print "Added %d users." % users_created_count
            print "%s users already existed." % (len(usernames) - users_created_count)
