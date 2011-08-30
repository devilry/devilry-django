from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option

from usermod import UserModCommand


class Command(UserModCommand):
    args = '<username>'
    help = 'Create new user.'
    option_list = BaseCommand.option_list + (
        make_option('--email',
            dest='email',
            default='',
            help='Email address'),
        make_option('--first_name',
            dest='first_name',
            default='',
            help='First name'),
        make_option('--last_name',
            dest='last_name',
            default='',
            help='Last name'),
        make_option('--superuser',
            action='store_true',
            dest='is_superuser',
            default=False,
            help='Make the user a superuser, with access to everything in the system.'),
    )

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Username is required. See --help.')
        verbosity = int(options.get('verbosity', '1'))
        username = args[0]
        kw = {}
        for attrname in ('email', 'first_name', 'last_name', 'is_superuser'):
            kw[attrname] = options[attrname]

        if User.objects.filter(username=username).count() == 0:
            user = User(username=username, **kw)
            user.set_unusable_password()
            self.save_user(user, verbosity)
        else:
            raise CommandError('User "{0}" already exists.'.format(username))
