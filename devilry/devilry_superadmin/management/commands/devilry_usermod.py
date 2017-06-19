from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from devilry.utils.management import add_input_encoding_argument


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
    help = 'Modify an existing user.'

    def add_arguments(self, parser):
        parser.add_argument(
            'shortname',
            default='',
            help='Shortname. The username if authenticating with username, '
                 'and email if not.'),
        parser.add_argument(
            '--full_name',
            dest='full_name',
            default=None,
            help='Full name'),
        parser.add_argument(
            '--superuser',
            action='store_true',
            dest='superuser',
            default=False,
            help='Make the user a superuser, with access to everything in the system.'),
        parser.add_argument(
            '--normaluser',
            action='store_true',
            dest='normaluser',
            default=False,
            help='Make the user a normal user, with access to everything that they are given explicit access to.'),
        add_input_encoding_argument(parser)

    def handle(self, *args, **options):
        self.inputencoding = options['inputencoding']
        verbosity = int(options.get('verbosity', '1'))
        kw = {}
        if options['superuser']:
            kw['is_superuser'] = True
        if options['normaluser']:
            kw['is_superuser'] = False

        try:
            user = get_user_model().objects.get(shortname=options['shortname'])
        except get_user_model().DoesNotExist:
            raise CommandError('User "{}" does not exist.'.format(options['shortname']))
        else:
            for key, value in kw.iteritems():
                setattr(user, key, value)
            if user.password == '':
                user.set_unusable_password()
            full_name = options.get('full_name')
            if full_name:
                user.fullname = unicode(full_name, self.inputencoding)
            user.full_clean()
            user.save()
            if verbosity > 0:
                print 'User "{}" saved successfully.'.format(user.shortname)
