from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option


class Command(BaseCommand):
    args = '[search|empty for all]'
    help = 'Search for a user by username. Matches any part of the username.'
    option_list = BaseCommand.option_list + (
        make_option('--username-only',
            action='store_true',
            dest='username_only',
            default=False,
            help='Only print usernames'),
        make_option('--superusers',
            action='store_true',
            dest='superusers',
            default=False,
            help='Only match superusers'),
        make_option('--normalusers',
            action='store_true',
            dest='normalusers',
            default=False,
            help='Only match non-superusers.'),
    )

    def handle(self, *args, **options):
        if len(args) == 1:
            qry = User.objects.filter(username__icontains=args[0])
        else:
            qry = User.objects.all()

        if options['superusers']:
            qry = qry.filter(is_superuser=True)
        if options['normalusers']:
            qry = qry.filter(is_superuser=False)

        for user in qry:
            if options['username_only']:
                print user.username
            else:
                self._print_user_details(user)

    def _print_user_details(self, user):
        print '{0}:'.format(user.username)
        for attrname in ('email', 'first_name', 'last_name', 'is_superuser',
                         'last_login', 'date_joined'):
            print '   {attrname}: {attr}'.format(attrname=attrname,
                                                 attr=getattr(user, attrname))
