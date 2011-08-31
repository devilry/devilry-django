from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from optparse import make_option


class UserModCommand(BaseCommand):
    def save_user(self, user, verbosity):
        try:
            user.full_clean()
        except ValidationError, e:
            errmsg = []
            for key, messages in e.message_dict.iteritems():
                errmsg.append('{0}: {1}'.format(key, ' '.join(messages)))
            raise CommandError('\n'.join(errmsg))
        user.save()
        if verbosity > 0:
            print 'User "{0}" saved successfully.'.format(user.username)


class Command(UserModCommand):
    args = '<username>'
    help = 'Create new user.'
    option_list = BaseCommand.option_list + (
        make_option('--email',
            dest='email',
            default=None,
            help='Email address'),
        make_option('--first_name',
            dest='first_name',
            default=None,
            help='First name'),
        make_option('--last_name',
            dest='last_name',
            default=None,
            help='Last name'),
        make_option('--superuser',
            action='store_true',
            dest='superuser',
            default=False,
            help='Make the user a superuser, with access to everything in the system.'),
        make_option('--normaluser',
            action='store_true',
            dest='normaluser',
            default=False,
            help='Make the user a normal user, with access to everything that they are given explicit access to.'),
    )

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Username is required. See --help.')
        verbosity = int(options.get('verbosity', '1'))
        username = args[0]
        kw = {}
        for attrname in ('email', 'first_name', 'last_name'):
            value = options[attrname]
            if value:
                kw[attrname] = value
        if options['superuser']:
            kw['is_superuser'] = True
        if options['normaluser']:
            kw['is_superuser'] = False

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('User "{0}" does not exist.'.format(username))
        else:
            for key, value in kw.iteritems():
                setattr(user, key, value)
            if user.password == '':
                user.set_unusable_password()
            self.save_user(user, verbosity)
