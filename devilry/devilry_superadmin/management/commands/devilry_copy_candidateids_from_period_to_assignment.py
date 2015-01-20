import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<subject-short_name> <period-short-name> <assignment-short-name>'
    help = 'Copy candidate ids from the table of student info on the period of ' \
        'the given assignment into the candidates already registered on the assignment.'

    def handle(self, *args, **options):
        from devilry.apps.core.models import Assignment

        if len(args) != 3:
            raise CommandError('Subject, Period and Assignment is required. See --help.')
        subject_short_name = args[0]
        period_short_name = args[1]
        assignment_short_name = args[2]

        try:
            assignment = Assignment.objects\
                .filter(
                    parentnode__parentnode__short_name=subject_short_name,
                    parentnode__short_name=period_short_name,
                    short_name=assignment_short_name)\
                .select_related('parentnode')\
                .get()
        except Assignment.DoesNotExist, e:
            raise CommandError('Could not find Assignment {}.{}.{}'.format(
                subject_short_name, period_short_name, assignment_short_name))
        else:

            # Print a warning for all relatedstudents without candidate ID
            for relatedstudent in assignment.period.relatedstudent_set\
                    .filter(candidate_id=None)\
                    .select_related('user'):
                logger.warning('User %s does not have a candidate ID registered on %s',
                               relatedstudent.user, assignment.period.get_path())

            # Get all candidate IDs and put them in a map with the user-id as key
            # and the candidate ID as value
            candidate_ids_by_userid = dict(assignment.period.relatedstudent_set\
                .exclude(candidate_id=None)\
                .values_list('user', 'candidate_id'))

            # Update the candidate ID of all where it is needed
            groups = assignment.assignmentgroups.all()\
                .prefetch_related('candidates', 'candidates__student')
            with transaction.commit_on_success():
                for group in groups:
                    for candidate in group.candidates.all():
                        if candidate.student.id in candidate_ids_by_userid:
                            candidate_id = candidate_ids_by_userid[candidate.student.id]
                            if candidate_id == candidate.candidate_id:
                                logger.info(
                                    'User with username=%s already has candiateID=%s - skipping.',
                                    candidate.student.username, candidate_id)
                            else:
                                candidate.candidate_id = candidate_id
                                candidate.save()
                                logger.info(
                                    'Added candidateID %s to user with username=%s.',
                                    candidate_id, candidate.student.username)
                        else:
                            logger.warning(
                                'Candidate with internal identifier %s (username=%s) does not have a '
                                'candidate ID. This may also happen if the student is not registered on %s',
                                candidate.id, candidate.student.username, assignment.period.get_path())
