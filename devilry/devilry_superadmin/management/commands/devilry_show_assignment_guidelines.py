import pprint
from django.core.management.base import BaseCommand
from devilry.apps.core.models.period import Period

from devilry.devilry_account.models import AssignmentGuidelinesLookupError, PeriodUserGuidelineAcceptance


class Command(BaseCommand):
    help = 'Show assignment guidelines - for debugging matching in the DEVILRY_ASSIGNMENT_GUIDELINES setting.'

    def add_arguments(self, parser):
        parser.add_argument(
            'period_path',
            help='The path to the period: "<subject short name>.<period short name>"')
        parser.add_argument(
            'devilryrole',
            choices=['student', 'examiner'],
            help='The devilry role to get guidelines for. One of: student, examiner')

    def handle(self, *args, **options):
        period_path = options['period_path']
        devilryrole = options['devilryrole']
        subject_short_name, period_short_name = period_path.split('.')
        period = Period.objects.get(
            short_name=period_short_name,
            parentnode__short_name=subject_short_name
        )
        try:
            self.stdout.write(self.style.SUCCESS(pprint.pformat(PeriodUserGuidelineAcceptance.objects.get_guidelines(
                period=period,
                devilryrole=devilryrole
            ))))
        except AssignmentGuidelinesLookupError as error:
            self.stdout.write(self.style.ERROR(str(error)))
