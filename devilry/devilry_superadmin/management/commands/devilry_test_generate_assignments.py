from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth import get_user_model

import arrow

from devilry.apps.core.models import Period, Assignment, Subject, RelatedStudent, RelatedExaminer, \
    Candidate, Examiner, AssignmentGroup
from devilry.devilry_account.models import SubjectPermissionGroup, PermissionGroup
from devilry.devilry_dbcache.models import AssignmentGroupCachedData
from devilry.devilry_group.models import GroupComment


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('ievvtasks_recreate_devdb')

        self.stdout.write('create SUBJECT')
        subject = Subject(
            short_name='ducktest',
            long_name='Duck TEST'
        )
        subject.full_clean()
        subject.save()

        subject_permissiongroup = SubjectPermissionGroup(
            subject=subject,
            permissiongroup=PermissionGroup.objects.get(name='The grandmas')
        )
        subject_permissiongroup.full_clean()
        subject_permissiongroup.save()

        #
        # PREVIOUS PERIOD
        #
        self.stdout.write('create PREVIOUS PERIOD')
        previous_period = Period(
            short_name='previous_period',
            long_name='Previous period',
            parentnode=subject,
            start_time=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=1,
                day=1,
                hour=0,
                minute=0,
                second=0
            ).datetime,
            end_time=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=6,
                day=30,
                hour=23,
                minute=59,
                second=59
            ).datetime
        )
        previous_period.full_clean()
        previous_period.save()

        # Previous relatedstudent
        previous_period_related_student = RelatedStudent(
            period=previous_period,
            user=get_user_model().objects.get(shortname='april@example.com')
        )
        previous_period_related_student.full_clean()
        previous_period_related_student.save()

        # Previous relatedexaminer
        previous_period_related_examiner = RelatedExaminer(
            period=previous_period,
            user=get_user_model().objects.get(shortname='thor@example.com')
        )
        previous_period_related_examiner.full_clean()
        previous_period_related_examiner.save()

        # Previous assignment1
        self.stdout.write('create PREVIOUS ASSIGNMENTS')
        previous_assignment1 = Assignment(
            short_name='assignment1',
            long_name='Assignment 1',
            parentnode=previous_period,
            first_deadline=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=1,
                day=15,
                hour=23,
                minute=59,
                second=59
            ).datetime,
            publishing_time=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=1,
                day=5,
                hour=0,
                minute=0,
                second=0
            ).datetime
        )
        previous_assignment1.full_clean()
        previous_assignment1.save()

        # Previous assignment1 group
        previous_period_assignment1_group = AssignmentGroup(
            parentnode=previous_assignment1
        )
        previous_period_assignment1_group.full_clean()
        previous_period_assignment1_group.save()
        
        # Previous assignment1 candidate
        previous_period_assignment1_group_candidate = Candidate(
            relatedstudent=previous_period_related_student,
            assignment_group=previous_period_assignment1_group
        )
        previous_period_assignment1_group_candidate.full_clean()
        previous_period_assignment1_group_candidate.save()

        # Previous assignment1 examiner
        previous_period_assignment1_group_examiner = Examiner(
            relatedexaminer=previous_period_related_examiner,
            assignmentgroup=previous_period_assignment1_group
        )
        previous_period_assignment1_group_examiner.full_clean()
        previous_period_assignment1_group_examiner.save()

        # Previous assignment1 publish passing result
        previous_period_assignment1_feedbackset = AssignmentGroupCachedData.objects \
            .get(group=previous_period_assignment1_group).last_feedbackset
        previous_period_assignment1_feedbackset_comment = GroupComment(
            feedback_set=previous_period_assignment1_feedbackset,
            part_of_grading=True,
            text='Good work on Assignment 1!',
            user_role=GroupComment.USER_ROLE_EXAMINER,
            comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT
        )
        # previous_period_assignment1_feedbackset_comment.full_clean()
        previous_period_assignment1_feedbackset_comment.save()
        previous_period_assignment1_feedbackset.grading_published_by = previous_period_related_examiner.user
        previous_period_assignment1_feedbackset.grading_points = 1
        previous_period_assignment1_feedbackset.grading_published_datetime = arrow.utcnow().to(settings.TIME_ZONE).replace(
            year=2021,
            month=1,
            day=17,
            hour=12,
            minute=0,
            second=0
        ).datetime
        previous_period_assignment1_feedbackset.full_clean()
        previous_period_assignment1_feedbackset.save()

        previous_assignment2 = Assignment(
            short_name='assignment2',
            long_name='Assignment 2',
            parentnode=previous_period,
            first_deadline=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=2,
                day=15,
                hour=23,
                minute=59,
                second=59
            ).datetime,
            publishing_time=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=2,
                day=5,
                hour=0,
                minute=0,
                second=0
            ).datetime
        )
        previous_assignment2.full_clean()
        previous_assignment2.save()

        # Previous assignment2 group
        previous_period_assignment2_group = AssignmentGroup(
            parentnode=previous_assignment2
        )
        previous_period_assignment2_group.full_clean()
        previous_period_assignment2_group.save()
        
        # Previous assignment2 candidate
        previous_period_assignment2_group_candidate = Candidate(
            relatedstudent=previous_period_related_student,
            assignment_group=previous_period_assignment2_group
        )
        previous_period_assignment2_group_candidate.full_clean()
        previous_period_assignment2_group_candidate.save()

        # Previous assignment2 examiner
        previous_period_assignment2_group_examiner = Examiner(
            relatedexaminer=previous_period_related_examiner,
            assignmentgroup=previous_period_assignment2_group
        )
        previous_period_assignment2_group_examiner.full_clean()
        previous_period_assignment2_group_examiner.save()        

        # Previous assignment2 publish passing result
        previous_period_assignment2_feedbackset = AssignmentGroupCachedData.objects \
            .get(group=previous_period_assignment2_group).last_feedbackset
        previous_period_assignment2_feedbackset_comment = GroupComment(
            feedback_set=previous_period_assignment2_feedbackset,
            part_of_grading=True,
            text='Good work on Assignment 2!',
            user_role=GroupComment.USER_ROLE_EXAMINER,
            comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT
        )
        # previous_period_assignment2_feedbackset_comment.full_clean()
        previous_period_assignment2_feedbackset_comment.save()
        previous_period_assignment2_feedbackset.grading_published_by = previous_period_related_examiner.user
        previous_period_assignment2_feedbackset.grading_points = 1
        previous_period_assignment2_feedbackset.grading_published_datetime = arrow.utcnow().to(settings.TIME_ZONE).replace(
            year=2021,
            month=2,
            day=17,
            hour=15,
            minute=0,
            second=0
        ).datetime
        previous_period_assignment2_feedbackset.full_clean()
        previous_period_assignment2_feedbackset.save()

        #
        # CURRENT PERIOD
        #
        self.stdout.write('create CURRENT PERIOD')
        current_period = Period(
            short_name='current_period',
            long_name='Current period',
            parentnode=subject,
            start_time=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=8,
                day=1,
                hour=12,
                minute=0,
                second=0
            ).datetime,
            end_time=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=12,
                day=31,
                hour=23,
                minute=59,
                second=59
            ).datetime
        )
        current_period.full_clean()
        current_period.save()

        # Current relatedstudent
        current_period_related_student = RelatedStudent(
            period=current_period,
            user=get_user_model().objects.get(shortname='april@example.com')
        )
        current_period_related_student.full_clean()
        current_period_related_student.save()
        
        # Current relatedexaminer
        current_period_related_examiner = RelatedExaminer(
            period=current_period,
            user=get_user_model().objects.get(shortname='thor@example.com')
        )
        current_period_related_examiner.full_clean()
        current_period_related_examiner.save()

        self.stdout.write('create CURRENT ASSIGNMENTS')
        current_assignment1 = Assignment(
            short_name='assignment1',
            long_name='Assignment 1',
            parentnode=current_period,
            first_deadline=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=8,
                day=15,
                hour=23,
                minute=59,
                second=59
            ).datetime,
            publishing_time=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=8,
                day=5,
                hour=0,
                minute=0,
                second=0
            ).datetime
        )
        current_assignment1.full_clean()
        current_assignment1.save()

        # Current assignment1 group
        current_period_assignment1_group = AssignmentGroup(
            parentnode=current_assignment1
        )
        current_period_assignment1_group.full_clean()
        current_period_assignment1_group.save()
        
        # Current assignment1 candidate
        current_period_assignment1_group_candidate = Candidate(
            relatedstudent=current_period_related_student,
            assignment_group=current_period_assignment1_group
        )
        current_period_assignment1_group_candidate.full_clean()
        current_period_assignment1_group_candidate.save()
        
        # Current assignment1 examiner
        current_period_assignment1_group_examiner = Examiner(
            relatedexaminer=current_period_related_examiner,
            assignmentgroup=current_period_assignment1_group
        )
        current_period_assignment1_group_examiner.full_clean()
        current_period_assignment1_group_examiner.save()

        # Previous assignment1 publish passing result
        current_period_assignment1_feedbackset = AssignmentGroupCachedData.objects \
            .get(group=current_period_assignment1_group).last_feedbackset
        current_period_assignment1_feedbackset_comment = GroupComment(
            feedback_set=current_period_assignment1_feedbackset,
            part_of_grading=True,
            text='Good work on Assignment 1!',
            user_role=GroupComment.USER_ROLE_EXAMINER,
            comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT
        )
        # current_period_assignment1_feedbackset_comment.full_clean()
        current_period_assignment1_feedbackset_comment.save()
        current_period_assignment1_feedbackset.grading_published_by = current_period_related_examiner.user
        current_period_assignment1_feedbackset.grading_points = 1
        current_period_assignment1_feedbackset.grading_published_datetime = arrow.utcnow().to(settings.TIME_ZONE).replace(
            year=2021,
            month=1,
            day=17,
            hour=12,
            minute=0,
            second=0
        ).datetime
        current_period_assignment1_feedbackset.full_clean()
        current_period_assignment1_feedbackset.save()

        current_assignment2 = Assignment(
            short_name='assignment2',
            long_name='Assignment 2',
            parentnode=current_period,
            first_deadline=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=9,
                day=15,
                hour=23,
                minute=59,
                second=59
            ).datetime,
            publishing_time=arrow.utcnow().to(settings.TIME_ZONE).replace(
                year=2021,
                month=9,
                day=5,
                hour=0,
                minute=0,
                second=0
            ).datetime
        )
        current_assignment2.full_clean()
        current_assignment2.save()
        
        # Current assignment2 group
        current_period_assignment2_group = AssignmentGroup(
            parentnode=current_assignment2
        )
        current_period_assignment2_group.full_clean()
        current_period_assignment2_group.save()
        
        # Current assignment2 candidate
        current_period_assignment2_group_candidate = Candidate(
            relatedstudent=current_period_related_student,
            assignment_group=current_period_assignment2_group
        )
        current_period_assignment2_group_candidate.full_clean()
        current_period_assignment2_group_candidate.save()
        
        # Current assignment2 examiner
        current_period_assignment2_group_examiner = Examiner(
            relatedexaminer=current_period_related_examiner,
            assignmentgroup=current_period_assignment2_group
        )
        current_period_assignment2_group_examiner.full_clean()
        current_period_assignment2_group_examiner.save()

        # Previous assignment1 publish passing result
        current_period_assignment2_feedbackset = AssignmentGroupCachedData.objects \
            .get(group=current_period_assignment2_group).last_feedbackset
        current_period_assignment2_feedbackset_comment = GroupComment(
            feedback_set=current_period_assignment2_feedbackset,
            part_of_grading=True,
            text='Good work on Assignment 1!',
            user_role=GroupComment.USER_ROLE_EXAMINER,
            comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT
        )
        # current_period_assignment2_feedbackset_comment.full_clean()
        current_period_assignment2_feedbackset_comment.save()
        current_period_assignment2_feedbackset.grading_published_by = current_period_related_examiner.user
        current_period_assignment2_feedbackset.grading_points = 1
        current_period_assignment2_feedbackset.grading_published_datetime = arrow.utcnow().to(settings.TIME_ZONE).replace(
            year=2021,
            month=9,
            day=17,
            hour=12,
            minute=0,
            second=0
        ).datetime
        current_period_assignment2_feedbackset.full_clean()
        current_period_assignment2_feedbackset.save()
