import arrow

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

from devilry.apps.core.models import Subject, Period, AssignmentGroup, Assignment, \
    RelatedExaminer, RelatedStudent, Candidate, Examiner
from devilry.devilry_dbcache.models import AssignmentGroupCachedData
from devilry.devilry_group.models import GroupComment
from devilry.devilry_comment.models import Comment


class Command(BaseCommand):
    help = 'Create test course.'

    def handle(self, *args, **options):
        # Create Subject
        self.stdout.write('Creating subject...')
        self.subject = Subject(
            short_name='stat-test',
            long_name='Statistics test'
        )
        self.subject.full_clean()
        self.subject.save()

        # Create Period
        self.stdout.write(f'Creating period for "{self.subject.long_name}"...')
        self.period = Period(
            parentnode=self.subject,
            short_name='stat-test-period',
            long_name='Statistics test period',
            start_time=arrow.get(datetime(2021, 8, 10, 23, 59, 59), settings.TIME_ZONE).datetime,
            end_time=arrow.get(datetime(2022, 6, 1, 23, 59, 59), settings.TIME_ZONE).datetime
        )
        self.period.full_clean()
        self.period.save()

        # Create Assignment
        self.stdout.write(f'Creating assignment for "{self.period.long_name}"...')
        self.assignment = Assignment(
            parentnode=self.period,
            short_name='stat-assignment0',
            long_name='Statistics assignment 0',
            publishing_time=arrow.get(datetime(2021, 8, 10, 23, 59, 59), settings.TIME_ZONE).datetime,
            first_deadline=arrow.get(datetime(2021, 8, 17, 23, 59, 59), settings.TIME_ZONE).datetime,
            max_points=10,
            passing_grade_min_points=3,
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS
        )
        self.assignment.full_clean()
        self.assignment.save()

        # Create examiners
        self.stdout.write(f'Creating RelatedExaminers for "{self.period.long_name}"...')
        self.examiner_user1 = get_user_model().objects.create_user(
            email='examiner1@example.com',
            password='test',
            fullname='Examiner User1')
        self.examiner_user2 = get_user_model().objects.create_user(
            email='examiner2@example.com',
            password='test',
            fullname='Examiner User2')
        self.examiner_user3 = get_user_model().objects.create_user(
            email='examiner3@example.com',
            password='test',
            fullname='Examiner User3')
        self.relatedexaminer1 = RelatedExaminer(
            period=self.period,
            user=self.examiner_user1)
        self.relatedexaminer1.full_clean()
        self.relatedexaminer1.save()
        self.relatedexaminer2 = RelatedExaminer(
            period=self.period,
            user=self.examiner_user2)
        self.relatedexaminer2.full_clean()
        self.relatedexaminer2.save()
        self.relatedexaminer3 = RelatedExaminer(
            period=self.period,
            user=self.examiner_user3)
        self.relatedexaminer3.full_clean()
        self.relatedexaminer3.save()

        # Create students
        student_num = 100
        self.stdout.write(f'Creating {student_num} RelatedStudents for "{self.period.long_name}"...')
        relatedstudent_list = []
        for num in range(student_num):
            studentuser = get_user_model().objects.create_user(
                email=f'student{num}@example.com',
                password='test',
                fullname=f'Student User{num}')
            relatedstudent = RelatedStudent(
                user=studentuser,
                period=self.period
            )
            relatedstudent.full_clean()
            relatedstudent.save()
            relatedstudent_list.append(relatedstudent)

        # Create AssignmentGroups for each relatedstudent
        self.stdout.write(f'Adding each student to their own AssignmentGroup for "{self.assignment.long_name}"...')
        assignmentgroup_list = []
        for relatedstudent in relatedstudent_list:
            assignmentgroup = AssignmentGroup(
                parentnode=self.assignment
            )
            assignmentgroup.full_clean()
            assignmentgroup.save()
            assignmentgroup.refresh_from_db()
            candidate = Candidate(
                relatedstudent=relatedstudent,
                assignment_group=assignmentgroup
            )
            candidate.full_clean()
            candidate.save()
            assignmentgroup_list.append(assignmentgroup)

        # Add all relatedexaminers to each AssignmentGroup.
        self.stdout.write(f'Adding all examiners to all AssignmentGroups for "{self.assignment.long_name}"...')
        for assignmentgroup in assignmentgroup_list:
            examiner = Examiner(
                assignmentgroup=assignmentgroup,
                relatedexaminer=self.relatedexaminer1
            )
            examiner.full_clean()
            examiner.save()
            examiner = Examiner(
                assignmentgroup=assignmentgroup,
                relatedexaminer=self.relatedexaminer2
            )
            examiner.full_clean()
            examiner.save()
            examiner = Examiner(
                assignmentgroup=assignmentgroup,
                relatedexaminer=self.relatedexaminer3
            )
            examiner.full_clean()
            examiner.save()

        # AssignmentGroup devilry and grading
        self.stdout.write(f'Adding student delivery and examiner grading for all groups on "{self.assignment.long_name}"...')
        for assignmentgroup in assignmentgroup_list:
            assignmentgroup_cached_data = AssignmentGroupCachedData.objects.get(group=assignmentgroup)
            last_feedbackset = assignmentgroup_cached_data.last_feedbackset

            # Add student comment
            delivery_comment_datetime = arrow.get(datetime(2021, 8, 15, 18, 00, 00), settings.TIME_ZONE).datetime
            student_user = Candidate.objects.get(assignment_group=assignmentgroup_cached_data.group).relatedstudent.user
            student_group_comment = GroupComment(
                feedback_set=last_feedbackset,
                user=student_user,
                text='Here is my delivery.',
                created_datetime=delivery_comment_datetime,
                published_datetime=delivery_comment_datetime,
                user_role=Comment.USER_ROLE_STUDENT,
                comment_type=Comment.COMMENT_TYPE_GROUPCOMMENT
            )
            student_group_comment.full_clean()
            student_group_comment.save()

            # Add examiner grading comment
            grading_comment_datetime = arrow.get(datetime(2021, 8, 16, 18, 00, 00), settings.TIME_ZONE).datetime
            examiner_group_comment = GroupComment(
                feedback_set=last_feedbackset,
                user=self.examiner_user1,
                text='This is your feedback.',
                created_datetime=grading_comment_datetime,
                published_datetime=grading_comment_datetime,
                user_role=Comment.USER_ROLE_EXAMINER,
                comment_type=Comment.COMMENT_TYPE_GROUPCOMMENT,
                part_of_grading=True
            )
            examiner_group_comment.full_clean()
            examiner_group_comment.save()
            last_feedbackset.grading_published_datetime = grading_comment_datetime
            last_feedbackset.grading_points = 5
            last_feedbackset.grading_published_by = examiner_group_comment.user
            last_feedbackset.full_clean()
            last_feedbackset.save()

