from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from devilry.utils.management import add_input_encoding_argument


class Command(BaseCommand):
    help = 'Create new user.'

    def add_arguments(self, parser):
        parser.add_argument(
            'username_v2_compat',
            default='',
            help='Username. Alias for --username for devilry v2 compatibility.'),
        parser.add_argument(
            '--username',
            dest='username',
            default='',
            help='Username. Must be specified if you use usernames for '
                 'authentication.'),
        parser.add_argument(
            '--email',
            dest='email',
            default='',
            help='Email address. Must be specified if you use emails for '
                 'authentication'),
        parser.add_argument(
            '--full_name',
            dest='full_name',
            default='',
            help='Full name'),
        parser.add_argument(
            '--superuser',
            action='store_true',
            dest='is_superuser',
            default=False,
            help='Make the user a superuser, with access to everything in the system.'),
        parser.add_argument(
            '--password',
            dest='password',
            default=False,
            help='Set a password for the user. If not specified, we set an unusable password.'),
        add_input_encoding_argument(parser)

    def handle(self, *args, **options):
        self.inputencoding = options['inputencoding']
        verbosity = int(options.get('verbosity', '1'))
        kwargs = {
            'email': options['email'],
            'username': options['username'] or options['username_v2_compat'],
            'is_superuser': options['is_superuser'],
            'fullname': options['full_name'],
            'password': options['password']
        }
        if settings.CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND:
            if not kwargs['email']:
                raise CommandError('email is required. See --help.')
        else:
            if not kwargs['username']:
                raise CommandError('username is required. See --help.')

        user, created = get_user_model().objects.get_or_create_user(**kwargs)
        if created and verbosity > 0:
            print('User "{0}" created successfully.'.format(user.shortname))
        else:
            raise CommandError('User "{0}" already exists.'.format(user.shortname))
