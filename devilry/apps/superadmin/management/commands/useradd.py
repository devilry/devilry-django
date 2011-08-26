from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option

class Command(BaseCommand):
    args = '<username>'
    help = 'Create new user.'
    option_list = BaseCommand.option_list + (
        make_option('--email',
            dest='email',
            default=False,
            help='Email address'),
        make_option('--first_name',
            dest='first_name',
            default=False,
            help='First name'),
        make_option('--last_name',
            dest='last_name',
            default=False,
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
        username = args[0]
        kw = {}
        for attrname in ('email', 'first_name', 'last_name'):
            kw[attrname] = options[attrname] or ''
        kw['is_superuser'] = options['is_superuser']
        self._add_user(username, **kw)

    def _add_user(self, username, **kw):
        if User.objects.filter(username=username).count() == 0:
            u = User(username=username, **kw)
            u.save()
            print 'User "{0}" created successfully.'.format(username)
        else:
            raise CommandError('User "{0}" already exists.'.format(username))
