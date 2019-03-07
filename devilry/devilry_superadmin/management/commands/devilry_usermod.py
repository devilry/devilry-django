from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from devilry.devilry_account.models import UserEmail
from devilry.utils.management import add_input_encoding_argument


class UserModCommand(BaseCommand):
    def save(self, obj):
        try:
            obj.full_clean()
        except ValidationError as e:
            errmsg = []
            for key, messages in e.message_dict.items():
                errmsg.append('{0}: {1}'.format(key, ' '.join(messages)))
            raise CommandError('\n'.join(errmsg))
        obj.save()

    def save_user(self, user, verbosity):
        self.save(user)
        if verbosity > 0:
            print('User "{0}" saved successfully.'.format(user.username))

    def save_profile(self, profile):
        self.save(profile)


class Command(UserModCommand):
    help = 'Modify an existing user.'

    def add_arguments(self, parser):
        parser.add_argument(
            'username_or_email',
            help='The username if authenticating with username, '
                 'and email if not.')
        parser.add_argument(
            '--email',
            help='An email address that will be added if it is not registered '
                 'for the user.')
        parser.add_argument(
            '--full_name',
            dest='full_name',
            default=None,
            help='Full name')
        parser.add_argument(
            '--superuser',
            action='store_true',
            dest='superuser',
            default=False,
            help='Make the user a superuser, with access to everything in the system.')
        parser.add_argument(
            '--normaluser',
            action='store_true',
            dest='normaluser',
            default=False,
            help='Make the user a normal user, with access to everything that they are given explicit access to.')
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
            if settings.CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND:
                user = get_user_model().objects.get_by_email(email=options['username_or_email'])
            else:
                user = get_user_model().objects.get_by_username(username=options['username_or_email'])
        except get_user_model().DoesNotExist:
            raise CommandError('User "{}" does not exist.'.format(options['username_or_email']))
        else:
            for key, value in kw.items():
                setattr(user, key, value)
            if user.password == '':
                user.set_unusable_password()
            full_name = options.get('full_name')
            if full_name:
                try:
                    user.fullname = str(full_name, self.inputencoding)
                except TypeError:
                    user.fullname = full_name
            if options['email']:
                if not user.useremail_set.filter(email=options['email']).exists():
                    useremail = UserEmail(
                        user=user,
                        email=options['email']
                    )
                    useremail.full_clean()
                    useremail.save()
            user.full_clean()
            user.save()
            if verbosity > 0:
                print('User "{}" saved successfully.'.format(user.shortname))
