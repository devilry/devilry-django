import os

from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from model_mommy import mommy

from devilry.devilry_account import models as account_models
from devilry.apps.core import models as core_models
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
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
        related_examiner = core_models.RelatedExaminer.objects.get(id=3)
        print(related_examiner.user)
        examiner = core_models.Examiner(relatedexaminer=related_examiner, assignmentgroup=group)
        examiner.save()

        ###############
        # First attempt
        ###############

        # set up first attempt
        first_deadline_datetime = datetime(year=2018, month=4, day=29, hour=14, tzinfo=timezone.get_current_timezone())
        last_feedbackset = group.cached_data.last_feedbackset
        last_feedbackset.deadline_datetime = first_deadline_datetime
        last_feedbackset.created_datetime = datetime(year=2018, month=4, day=23, hour=14, tzinfo=timezone.get_current_timezone())
        last_feedbackset.save()

        # student add delivery
        student_comment_publish_time = datetime(year=2018, month=4, day=29, hour=13, tzinfo=timezone.get_current_timezone())
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
        examiner_feedback_comment1 = mommy.make('devilry_group.GroupComment',
                                               text='Failed because... Try again',
                                               part_of_grading=True,
                                               feedback_set=last_feedbackset,
                                               user=related_examiner.user,
                                               user_role=group_models.GroupComment.USER_ROLE_EXAMINER)
        last_feedbackset.publish(published_by=related_examiner.user, grading_points=0)
        last_feedbackset.grading_published_datetime = datetime(year=2018, month=4, day=29, hour=15, minute=1, tzinfo=timezone.get_current_timezone())
        last_feedbackset.save()
        group_models.GroupComment.objects.filter(id=examiner_feedback_comment1.id)\
            .update(published_datetime=datetime(year=2018, month=4, day=29, hour=15, minute=2, tzinfo=timezone.get_current_timezone()))
        group_models.GroupComment.objects.filter(id=examiner_feedback_comment1.id)\
            .update(created_datetime=datetime(year=2018, month=4, day=29, hour=15, minute=2, tzinfo=timezone.get_current_timezone()))
        asd = group_models.GroupComment.objects.filter(id=examiner_feedback_comment1.id).get()
        print(asd.created_datetime)
        print(timezone.now())
        asd.created_datime = timezone.now()
        asd.save()
        print(asd.created_datetime)
        # examiner_feedback_comment1.published_datetime = first_deadline_datetime + timezone.timedelta(hours=4)
        # examiner_feedback_comment1.created_datetime = first_deadline_datetime + timezone.timedelta(hours=4)
        # examiner_feedback_comment1.save()




        ################
        # Second attempt
        ################

        # setup second attempt
        second_deadline_datetime = timezone.now() - timezone.timedelta(days=5)
        second_feedbackset = mommy.make('devilry_group.FeedbackSet',
                                        group=group,
                                        feedbackset_type=group_models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
                                        created_datetime=first_deadline_datetime + timezone.timedelta(hours=4),
                                        deadline_datetime=second_deadline_datetime)

        # student add second delivery
        now = timezone.now()
        student_comment_publish_time = now - timezone.timedelta(days=5, hours=1)
        student_comment = mommy.make('devilry_group.GroupComment',
                                     text='Here\'s my second delivery!',
                                     feedback_set=second_feedbackset,
                                     user=student_user,
                                     user_role=group_models.GroupComment.USER_ROLE_STUDENT,
                                     created_datetime=student_comment_publish_time,
                                     published_datetime=student_comment_publish_time)
        student_comment_file = mommy.make('devilry_comment.CommentFile',
                                          comment=student_comment, filename='delivery2.py', filesize=0,
                                          created_datetime=student_comment_publish_time)

        # examiner corrects second attempt
        examiner_feedback_comment2 = mommy.make('devilry_group.GroupComment',
                                               text='Well done!',
                                               part_of_grading=True,
                                               feedback_set=second_feedbackset,
                                               user=related_examiner.user,
                                               user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                                               visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        second_feedbackset.publish(published_by=related_examiner.user, grading_points=1)
        publish_timestamp = second_deadline_datetime + timezone.timedelta(hours=3)
        second_feedbackset.grading_published_datetime = publish_timestamp
        second_feedbackset.save()
        timestamp = now - timezone.timedelta(days=4, hours=20)
        group_models.GroupComment.objects.filter(id=examiner_feedback_comment2.id).update(published_datetime=timestamp)
        group_models.GroupComment.objects.filter(id=examiner_feedback_comment2.id).update(created_datetime=timestamp)

        # examiner_feedback_comment2.published_datetime = second_deadline_datetime + timezone.timedelta(hours=4)
        # examiner_feedback_comment2.created_datetime = second_deadline_datetime + timezone.timedelta(hours=4)
        # examiner_feedback_comment2.save()

        group_models.FeedbackSetDeadlineHistory.objects.all().delete()
        group_models.FeedbackSetGradingUpdateHistory.objects.all().delete()

        self.__print_group_feed_representation(group=group)