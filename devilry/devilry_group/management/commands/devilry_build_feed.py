import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from model_mommy import mommy

from devilry.devilry_account import models as account_models
from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models


class Command(BaseCommand):
    student_shortname = 'teststudent@example.com'
    student_fullname = 'Test Student'
    student_lastname = 'Student'

    def __create_student_user(self):
        user = mommy.make(settings.AUTH_USER_MODEL,
                          shortname=self.student_shortname,
                          fullname=self.student_fullname,
                          lastname=self.student_lastname)
        mommy.make('devilry_account.UserEmail', user=user, email=self.student_shortname, is_primary=True)
        mommy.make('devilry_account.UserName', user=user, username=self.student_shortname, is_primary=True)
        user.set_password('test')
        return user

    def __create_candidate_and_group(self, user):
        assignment = core_models.Assignment.objects.get(id=5)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        relatedstudent = mommy.make('core.RelatedStudent', user=user, period=assignment.parentnode)
        mommy.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=group)
        return group

    def __print_group_feed_representation(self, group):
        for feedback_set in group.feedbackset_set.order_by('deadline_datetime'):
            print('* FeedbackSet {}*'.format(feedback_set.deadline_datetime))
            for group_comment in feedback_set.groupcomment_set.order_by('published_datetime'):
                print('\tComment: {} - {}'.format(group_comment.user, group_comment.published_datetime))
                for comment_file in group_comment.commentfile_set.order_by('created_datetime'):
                    print('\t\tComment file - {}'.format(comment_file.filename))

    def handle(self, *args, **options):
        student_user = self.__create_student_user()
        group = self.__create_candidate_and_group(user=student_user)
        related_examiner = core_models.RelatedExaminer.objects.get(id=1)
        examiner = core_models.Examiner(relatedexaminer=related_examiner, assignmentgroup=group)
        examiner.save()

        # set up first attempt
        first_deadline_datetime = timezone.now() - timezone.timedelta(days=10)
        last_feedbackset = group.cached_data.last_feedbackset
        last_feedbackset.deadline_datetime = first_deadline_datetime
        last_feedbackset.save()

        # student add delivery
        student_comment_publish_time = timezone.now() - timezone.timedelta(days=10, hours=1)
        student_comment = mommy.make('devilry_group.GroupComment',
                                     text='Here\'s my delivery!',
                                     feedback_set=last_feedbackset,
                                     user=student_user,
                                     user_role=group_models.GroupComment.USER_ROLE_STUDENT,
                                     created_datetime=student_comment_publish_time,
                                     published_datetime=student_comment_publish_time)
        student_comment_file = mommy.make('devilry_comment.CommentFile',
                                          comment=student_comment, filename='delivery.py', filesize=0,
                                          created_datetime=student_comment_publish_time)

        # examiner correct first attempt.
        last_feedbackset.publish(published_by=related_examiner.user, grading_points=0)
        examiner_feedback_comment = mommy.make('devilry_group.GroupComment',
                                               text='Failed because... Try again',
                                               feedback_set=last_feedbackset,
                                               user=related_examiner.user,
                                               user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                                               created_datetime=first_deadline_datetime + timezone.timedelta(hours=3),
                                               published_datetime=first_deadline_datetime + timezone.timedelta(hours=3))

        self.__print_group_feed_representation(group=group)