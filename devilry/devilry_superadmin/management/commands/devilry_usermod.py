from optparse import make_option
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand, CommandError

from django.core.exceptions import ValidationError

from devilry.utils.management import make_input_encoding_option


class UserModCommand(BaseCommand):
    def save(self, obj):
        try:
            obj.full_clean()
        except ValidationError, e:
            errmsg = []
            for key, messages in e.message_dict.iteritems():
                errmsg.append('{0}: {1}'.format(key, ' '.join(messages)))
            raise CommandError('\n'.join(errmsg))
        obj.save()

    def save_user(self, user, verbosity):
        self.save(user)
        if verbosity > 0:
            print 'User "{0}" saved successfully.'.format(user.username)

    def save_profile(self, profile):
        self.save(profile)


class Command(UserModCommand):
    args = '<username>'
    help = 'Create new user.'
    option_list = BaseCommand.option_list + (
        make_option('--email',
                    dest='email',
                    default=None,
                    help='Email address'),
        make_option('--full_name',
                    dest='full_name',
                    default=None,
                    help='Full name'),
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
        make_input_encoding_option()
    )

    def handle(self, *args, **options):
        self.inputencoding = options['inputencoding']
        if len(args) != 1:
            raise CommandError('Username is required. See --help.')
        verbosity = int(options.get('verbosity', '1'))
        username = args[0]
        kw = {}
        for attrname in ('email',):
            value = options[attrname]
            if value:
                kw[attrname] = value
        if options['superuser']:
            kw['is_superuser'] = True
            kw['is_staff'] = True
        if options['normaluser']:
            kw['is_superuser'] = False
            kw['is_staff'] = False

        try:
            user = get_user_model().objects.get(shortname=username)
        except get_user_model().DoesNotExist:
            raise CommandError('User "{0}" does not exist.'.format(username))
        else:
            for key, value in kw.iteritems():
                setattr(user, key, value)
            if user.password == '':
                user.set_unusable_password()
            full_name = options.get('full_name')
            if full_name:
                user.fullname = unicode(full_name, self.inputencoding)
            self.save_user(user, verbosity)
