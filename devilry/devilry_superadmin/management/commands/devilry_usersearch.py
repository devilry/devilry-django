from optparse import make_option
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand

from devilry.utils.management import make_output_encoding_option


class Command(BaseCommand):
    args = '[search|empty for all]'
    help = 'Search for a user by username. Matches any part of the username.'
    option_list = BaseCommand.option_list + (
        make_option('--username-only',
                    action='store_true',
                    dest='username_only',
                    default=False,
                    help='Only print usernames'),
        make_option('--no-email',
                    action='store_true',
                    dest='noemail',
                    default=False,
                    help='Only match users without an email address.'),
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
        make_output_encoding_option()
    )

    def handle(self, *args, **options):
        self.outputencoding = options['outputencoding']
        if len(args) == 1:
            qry = get_user_model().objects.filter(username__icontains=args[0])
        else:
            qry = get_user_model().objects.all()

        if options['superusers']:
            qry = qry.filter(is_superuser=True)
        if options['normalusers']:
            qry = qry.filter(is_superuser=False)
        if options['noemail']:
            qry = qry.filter(email='')

        for user in qry:
            if options['username_only']:
                print user.username
            else:
                self._print_user_details(user)

    def _print_user_details(self, user):
        print '{0}:'.format(user.username)
        for attrname in ('email', 'is_superuser',
                         'last_login', 'date_joined', 'fullname'):
            attr = getattr(user, attrname)
            if isinstance(attr, str) or isinstance(attr, unicode):
                attr = attr.encode(self.outputencoding)
            print '   {attrname}: {attr}'.format(attrname=attrname,
                                                 attr=attr)
