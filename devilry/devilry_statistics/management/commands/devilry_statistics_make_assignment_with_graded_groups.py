import random
from random import randint

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from devilry.apps.core import models as coremodels
from devilry.devilry_group import models as group_models


class Command(BaseCommand):
    """
    Management script for anonymizing the database.
    """
    help = 'Anonymize the entire database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--random',
            dest='random',
            default=False,
            action='store_true'
        )
        parser.add_argument(
            '--subject-name',
            default='statistics_subject',
            dest='subject_name'
        )
        parser.add_argument(
            '--period-name',
            default='statistics_period',
            dest='period_name'
        )
        parser.add_argument(
            '--assignment-name',
            default='statistics_assignment',
            dest='assignment_name'
        )
        parser.add_argument(
            '--num-students',
            default=10,
            type=int,
            dest='num_students'
        )

    def random_generate(self, **options):
        subject_name = options['subject_name']
        period_name = options['period_name']
        assignment_name = options['assignment_name']
        num_students = options['num_students']

        with transaction.atomic():
            subject = coremodels.Subject(
                long_name=subject_name,
                short_name='stat_subject'
            )
            subject.save()

            period_start_time = timezone.now() - timezone.timedelta(days=50)
            period_end_time = timezone.now() + timezone.timedelta(days=50)
            period = coremodels.Period(
                long_name=period_name,
                short_name='stat_period',
                start_time=period_start_time,
                end_time=period_end_time,
                parentnode=subject
            )
            period.save()

            assignment_publishing_time = period_start_time + timezone.timedelta(days=3)
            assignment = coremodels.Assignment(
                long_name=assignment_name,
                short_name='stat_assignment',
                publishing_time=assignment_publishing_time,
                first_deadline=assignment_publishing_time + timezone.timedelta(days=7),
                points_to_grade_mapper=coremodels.Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
                max_points=50,
                parentnode=period
            )
            assignment.save()

            relatedexaminers = []
            for num in range(10):
                examiner_user = get_user_model()(
                    fullname='Examiner#{}'.format(num),
                    shortname='examiner#{}@example.com'.format(num)
                )
                examiner_user.save()
                print(('Create examineruser#{}'.format(num)))
                relatedexaminer = coremodels.RelatedExaminer(
                    user=examiner_user,
                    period=period
                )
                relatedexaminer.save()
                relatedexaminers.append(relatedexaminer.id)

            grading_published_datetime = assignment_publishing_time + timezone.timedelta(days=8)
            assignment_groups = []

            # Create assignment groups and add students
            for num in range(num_students):
                assignment_group = coremodels.AssignmentGroup(
                    parentnode=assignment
                )
                assignment_group.save()
                print(('Create assignment group#{}'.format(num)))

                student_user = get_user_model()(
                    fullname='Student#{}'.format(num),
                    shortname='student#{}@example.com'.format(num)
                )
                student_user.save()
                print(('Create studentuser#{}'.format(num)))
                relatedstudent = coremodels.RelatedStudent(
                    user=student_user,
                    period=period
                )
                relatedstudent.save()
                print(('Create relatedstudent#{}'.format(num)))
                coremodels.Candidate(
                    relatedstudent=relatedstudent,
                    assignment_group=assignment_group
                ).save()
                print(('Create candidate#{}'.format(num)))

                assignment_groups.append(assignment_group.id)

            # Random organize examiners
            relatedexaminer_ids = [relatedexaminer_id for relatedexaminer_id in relatedexaminers]
            assignmentgroup_ids = [group_id for group_id in assignment_groups]
            random.shuffle(relatedexaminer_ids)
            random.shuffle(assignmentgroup_ids)
            examiners_to_create = []
            while assignmentgroup_ids:
                for relatedexaminer_id in relatedexaminers:
                    if not assignmentgroup_ids:
                        break
                    examiners_to_create.append(
                        coremodels.Examiner(relatedexaminer_id=relatedexaminer_id,
                                            assignmentgroup_id=assignmentgroup_ids.pop(0))
                    )
            coremodels.Examiner.objects.bulk_create(examiners_to_create)

            # Set grading on groups
            for group_id in assignment_groups:
                if randint(0, 1) == 1:
                    feedbackset = group_models.FeedbackSet.objects.get(group_id=group_id)
                    feedbackset.grading_published_datetime = grading_published_datetime
                    feedbackset.grading_points = randint(0, assignment.max_points)
                    feedbackset.save()

    def create_group_with_student_and_examiner(self,
                                               relatedexaminer,
                                               student_shortname,
                                               student_fullname,
                                               assignment,
                                               grading_points=None):
        assignment_group = coremodels.AssignmentGroup(
            parentnode=assignment
        )
        assignment_group.save()

        # Create student
        student_user = get_user_model()(
            fullname=student_fullname,
            shortname=student_shortname
        )
        student_user.save()
        relatedstudent = coremodels.RelatedStudent(
            user=student_user,
            period=assignment.parentnode
        )
        relatedstudent.save()
        coremodels.Candidate(
            relatedstudent=relatedstudent,
            assignment_group=assignment_group
        ).save()

        # Create examiner
        coremodels.Examiner(
            relatedexaminer=relatedexaminer,
            assignmentgroup=assignment_group
        ).save()

        # publish grading
        if grading_points is not None:
            grading_published_datetime = assignment.publishing_time + timezone.timedelta(days=8)
            feedbackset = group_models.FeedbackSet.objects.get(group_id=assignment_group.id)
            feedbackset.grading_published_datetime = grading_published_datetime
            feedbackset.grading_points = grading_points
            feedbackset.save()

    def handle(self, *args, **options):
        random = options['random']
        subject_name = options['subject_name']
        period_name = options['period_name']
        assignment_name = options['assignment_name']
        num_students = options['num_students']

        if random:
            self.random_generate(
                subject_name=subject_name,
                period_name=period_name,
                assignment_name=assignment_name,
                num_students=num_students)
        else:
            subject = coremodels.Subject(
                long_name=subject_name,
                short_name='stat_subject'
            )
            subject.save()

            period_start_time = timezone.now() - timezone.timedelta(days=50)
            period_end_time = timezone.now() + timezone.timedelta(days=50)
            period = coremodels.Period(
                long_name=period_name,
                short_name='stat_period',
                start_time=period_start_time,
                end_time=period_end_time,
                parentnode=subject
            )
            period.save()

            assignment_publishing_time = period_start_time + timezone.timedelta(days=3)
            assignment = coremodels.Assignment(
                long_name=assignment_name,
                short_name='stat_assignment',
                publishing_time=assignment_publishing_time,
                first_deadline=assignment_publishing_time + timezone.timedelta(days=7),
                points_to_grade_mapper=coremodels.Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
                max_points=50,
                passing_grade_min_points=20,
                parentnode=period
            )
            assignment.save()

            # Examiner 1
            examiner_user = get_user_model()(
                fullname='Examiner1',
                shortname='examiner1@example.com'
            )
            examiner_user.save()
            relatedexaminer = coremodels.RelatedExaminer(
                user=examiner_user,
                period=assignment.parentnode
            )
            relatedexaminer.save()
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student1@example.com',
                student_fullname='Student1',
                assignment=assignment,
                grading_points=30)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student2@example.com',
                student_fullname='Student2',
                assignment=assignment,
                grading_points=30)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student3@example.com',
                student_fullname='Student3',
                assignment=assignment,
                grading_points=30)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student4@example.com',
                student_fullname='Student4',
                assignment=assignment,
                grading_points=10)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student5@example.com',
                student_fullname='Student5',
                assignment=assignment,
                grading_points=10)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student6@example.com',
                student_fullname='Student6',
                assignment=assignment)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student7@example.com',
                student_fullname='Student7',
                assignment=assignment)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student8@example.com',
                student_fullname='Student8',
                assignment=assignment)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student9@example.com',
                student_fullname='Student9',
                assignment=assignment)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student10@example.com',
                student_fullname='Student10',
                assignment=assignment)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student11@example.com',
                student_fullname='Student11',
                assignment=assignment)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student12@example.com',
                student_fullname='Student12',
                assignment=assignment)
            self.create_group_with_student_and_examiner(
                relatedexaminer=relatedexaminer,
                student_shortname='student13@example.com',
                student_fullname='Student13',
                assignment=assignment)

            # call_command('ievvtasks_set_all_passwords_to_test')
