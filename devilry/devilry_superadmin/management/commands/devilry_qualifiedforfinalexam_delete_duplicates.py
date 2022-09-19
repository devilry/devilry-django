from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from devilry.devilry_qualifiesforexam.models import QualifiesForFinalExam
from devilry.apps.core.models import Period


def get_qualifiesforfinalexam_collision_periods(user_a, user_b):
    periods = set()
    for period_id in QualifiesForFinalExam.objects.filter(relatedstudent__user=user_a).values_list('relatedstudent__period_id', flat=True).distinct('relatedstudent__period_id'):
        period = Period.objects.get(id=period_id)
        if QualifiesForFinalExam.objects.filter(relatedstudent__user=user_b, relatedstudent__period=period_id).exists():
            periods.add(period)
    return list(sorted(periods, key=lambda p: p.get_path()))


def select_username_to_delete(user_a, user_b, period):
    selected_shortname = input(f'Select which user to DELETE qualifies for final exam results for in {period.get_path()} [{user_a.shortname}|{user_b.shortname}]: ').strip()
    if selected_shortname == user_a.shortname:
        return user_a
    elif selected_shortname == user_b.shortname:
        return user_b
    print(f'[ERROR] Invalid choice: {selected_shortname}')
    return select_username_to_delete(user_a, user_b, period)


class Command(BaseCommand):
    help = (
        'Delete qualified-for-final-exam duplicate results for one or more users. This a DESCRUCTIVE action, '
        'but each change has to be confirmed interactively. '
        'You typically use this along with "devilry_usermerge" to merge two users. I.e.: '
        'you run this script first to select the qualified-for-final-exam results to keep '
        'when both users have results for the same period, then run devilry_usermerge.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-a',
            required=True,
            dest='user_a_identifier',
            help='The username/email (depending on what the devilry instance is configured to use as identifier) for the first user.'
        )
        parser.add_argument(
            '--user-b',
            dest='user_b_identifier',
            required=True,
            help=(
                'The username/email (depending on what the devilry instance is configured to use as identifier) for the second user.'
            )
        )
        parser.add_argument(
            '--preview',
            action='store_true',
            dest='preview',
            default=False,
            help=(
                'Preview all possible changes without changing anything.')
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
        user_a = self._get_user_from_identifier(options['user_a_identifier'])
        user_b = self._get_user_from_identifier(options['user_b_identifier'])
        preview = options['preview']
        collision_periods = get_qualifiesforfinalexam_collision_periods(user_a, user_b)
        for period in collision_periods:
            self.stdout.write('')
            self.stdout.write('')
            self.stdout.write(f'## Period: {period.get_path()}')
            qualifiesforfinalexam_queryset = QualifiesForFinalExam.objects\
                        .filter(relatedstudent__period=period)\
                        .select_related('status') \
                        .order_by('status__createtime')
            for user in user_a, user_b:
                self.stdout.write('')
                self.stdout.write(f'{user.shortname} ({period.get_path()}):')
                for qualifiesforfinalexam in qualifiesforfinalexam_queryset.filter(relatedstudent__user=user):
                    self.stdout.write(
                        f'- Qualifies: {bool(qualifiesforfinalexam.qualifies)} '
                        f'[status:{qualifiesforfinalexam.status.status}, '
                        f'created time:{qualifiesforfinalexam.status.createtime}, '
                        f'exported time:{qualifiesforfinalexam.status.exported_timestamp}]')
            
            self.stdout.write('')
            if preview:
                self.stdout.write('--- Would ask which one to keep here of not in preview mode ---')
            else:
                user_to_delete = select_username_to_delete(
                    user_a=user_a, user_b=user_b, period=period)
                for qualifiesforfinalexam in qualifiesforfinalexam_queryset.filter(relatedstudent__user=user_to_delete):
                    qualifiesforfinalexam.smart_delete()
