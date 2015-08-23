from optparse import make_option
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand, CommandError

from devilry.devilry_superadmin.management.commands.devilry_usermod import UserModCommand
from devilry.utils.management import make_input_encoding_option


class Command(UserModCommand):
    args = '<username>'
    help = 'Create new user.'
    option_list = BaseCommand.option_list + (
        make_option('--email',
                    dest='email',
                    default='',
                    help='Email address'),
        make_option('--full_name',
                    dest='full_name',
                    default='',
                    help='Full name'),
        make_option('--superuser',
                    action='store_true',
                    dest='is_superuser',
                    default=False,
                    help='Make the user a superuser, with access to everything in the system.'),
        make_option('--password',
                    dest='password',
                    default=False,
                    help='Set a password for the user. If not specified, we set an unusable password.'),
        make_input_encoding_option()
    )

    def handle(self, *args, **options):
        self.inputencoding = options['inputencoding']
        if len(args) != 1:
            raise CommandError('Username is required. See --help.')
        verbosity = int(options.get('verbosity', '1'))
        username = args[0]
        kw = {}
        for attrname in ('email', 'is_superuser'):
            kw[attrname] = options[attrname]
        if options['is_superuser']:
            kw['is_staff'] = True

        if get_user_model().objects.filter(username=username).count() == 0:
            user = get_user_model()(username=username, **kw)
            full_name = options.get('full_name')
            if full_name:
                user.fullname = unicode(full_name, self.inputencoding)
            if options['password']:
                user.set_password(options['password'])
            else:
                user.set_unusable_password()
            self.save_user(user, verbosity)
        else:
            raise CommandError('User "{0}" already exists.'.format(username))
