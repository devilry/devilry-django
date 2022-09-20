import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from devilry.devilry_account.user_merger import UserMerger
from devilry.devilry_superadmin.management.commands.devilry_qualifiedforfinalexam_delete_duplicates import get_qualifiesforfinalexam_collision_periods


class Command(BaseCommand):
    help = (
        'Merge two users. Warning: This is just a partial merge. It just moves all '
        'the student related stuff, and most of the examiner related stuff + admin permissions. It DOES NOT '
        'change all meta-relations like created_by foreign keys on various database objects. '
        'Should be good enough to get the essential data moved from one user into another.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-user',
            required=True,
            dest='source_user_identifier',
            help='The username/email (depending on what the devilry instance is configured to use as identifier) for the source user.'
        )
        parser.add_argument(
            '--target-user',
            dest='target_user_identifier',
            required=True,
            help=(
                'The username/email (depending on what the devilry instance is configured to use as identifier) for the target user. '
                'The target user is the user that will receive ownership of objects belonging to source user after the merge.'
            )
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help=(
                'Verbose summary of changes. Prints out the same summary as the one stored in the '
                'MergedUser model for the merge instead of just the short(er) summary.')
        )

    def _get_user_from_identifier(self, user_identifier):
        try:
            if settings.CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND:
                return get_user_model().objects.get_by_email(email=user_identifier)
            else:
                return get_user_model().objects.get_by_username(username=user_identifier)
        except get_user_model().DoesNotExist:
            raise CommandError('User {identifier!r} does not exist.')

    def handle(self, *args, **options):
        source_user = self._get_user_from_identifier(options['source_user_identifier'])
        target_user = self._get_user_from_identifier(options['target_user_identifier'])
        if get_qualifiesforfinalexam_collision_periods(source_user, target_user):
            self.stderr.write(
                f'[ERROR] There are collisions in qualifies for final exam between {source_user} and {target_user}. '
                f'Please use ``python manage.py devilry_qualifiedforfinalexam_delete_duplicates`` to resolve the conflicts '
                f'before attempting the merge.')
            raise SystemExit()
        verbose = options['verbose']
        pretend_merger = UserMerger(source_user=source_user, target_user=target_user, pretend=True)
        pretend_merger.merge()

        self.stdout.write('Merge summary:')
        self.stdout.write(self.style.WARNING('*' * 70))
        self.stdout.write(f'Source user: {source_user.get_displayname()}')
        self.stdout.write(f'Target user: {target_user.get_displayname()}')
        self.stdout.write(f'Merge summary:')
        if verbose:
            summary = pretend_merger.merged_user.summary_json
        else:
            summary = pretend_merger.merged_user.short_summary_json
        self.stdout.write(json.dumps(summary, indent=2, sort_keys=True))
        self.stdout.write(self.style.WARNING('*' * 70))
        if input('Do you want to apply these changes? yes|NO: ').strip() == 'yes':
            UserMerger(source_user=source_user, target_user=target_user, pretend=False).merge()
        else:
            raise CommandError('Aborted')