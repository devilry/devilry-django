import mock
from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from model_mommy import mommy

from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.timeline_builder.feedbackfeed_timeline_builder import FeedbackFeedTimelineBuilder
from devilry.devilry_group.views.feedbackfeed_admin import AdminFeedbackFeedView
from devilry.devilry_group.views import feedbackfeed_examiner as examiner_views
from devilry.devilry_group.views.feedbackfeed_student import StudentFeedbackFeedView
from devilry.devilry_group import models as group_models


class TestFeedbackFeedTimelineBuilder(TestCase, object):

    def test_student_timelinebuilder_one_feedbackset_last_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        timeline_builder = FeedbackFeedTimelineBuilder(StudentFeedbackFeedView())
        timeline = timeline_builder.build_timeline(feedbackset.group, [feedbackset])
        self.assertEquals(timeline[0], feedbackset.group.assignment.first_deadline)

    def test_student_timelinebuilder_two_feedbacksets_last_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  is_last_in_group=None,
                                  group__parentnode=assignment)
        feedbackset2 = mommy.make('devilry_group.FeedbackSet',
                                  group=feedbackset1.group,
                                  deadline_datetime=timezone.now())
        timeline_builder = FeedbackFeedTimelineBuilder(StudentFeedbackFeedView())
        timeline = timeline_builder.build_timeline(feedbackset1.group, [feedbackset1, feedbackset2])
        self.assertEquals(timeline[0], feedbackset2.deadline_datetime)

    def test_examiner_timelinebuilder_one_feedbackset_last_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(examiner_views.ExaminerBaseFeedbackFeedView(request=mockrequest))
        timeline = timeline_builder.build_timeline(feedbackset.group, [feedbackset])
        self.assertEquals(timeline[0], feedbackset.group.assignment.first_deadline)

    def test_examiner_timelinebuilder_two_feedbacksets_last_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  is_last_in_group=None,
                                  group__parentnode=assignment)
        feedbackset2 = mommy.make('devilry_group.FeedbackSet',
                                  group=feedbackset1.group,
                                  deadline_datetime=timezone.now())
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(examiner_views.ExaminerBaseFeedbackFeedView(request=mockrequest))
        timeline = timeline_builder.build_timeline(feedbackset1.group, [feedbackset1, feedbackset2])
        self.assertEquals(timeline[0], feedbackset2.deadline_datetime)

    def test_admin_timelinebuilder_one_feedbackset_last_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        timeline_builder = FeedbackFeedTimelineBuilder(AdminFeedbackFeedView())
        timeline = timeline_builder.build_timeline(feedbackset.group, [feedbackset])
        self.assertEquals(timeline[0], feedbackset.group.assignment.first_deadline)

    def test_admin_timelinebuilder_two_feedbacksets_last_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  is_last_in_group=None,
                                  group__parentnode=assignment)
        feedbackset2 = mommy.make('devilry_group.FeedbackSet',
                                  group=feedbackset1.group,
                                  deadline_datetime=timezone.now())
        timeline_builder = FeedbackFeedTimelineBuilder(AdminFeedbackFeedView())
        timeline = timeline_builder.build_timeline(feedbackset1.group, [feedbackset1, feedbackset2])
        self.assertEquals(timeline[0], feedbackset2.deadline_datetime)

    def test_get_feedbacksets_for_group(self):
        timelinebuilder = FeedbackFeedTimelineBuilder(None)
        group = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet', group=group, is_last_in_group=None,)
        mommy.make('devilry_group.FeedbackSet', group=group, is_last_in_group=None,)
        mommy.make('devilry_group.FeedbackSet', group=group, is_last_in_group=None,)
        mommy.make('devilry_group.FeedbackSet', group=group, is_last_in_group=None,)
        mommy.make('devilry_group.FeedbackSet', group=group)

        self.assertEquals(5, len(timelinebuilder.get_feedbacksets_for_group(group)))

    def test_student_add_comments_to_timeline_all_visible_to_everyone(self):
        timeline_builder = FeedbackFeedTimelineBuilder(StudentFeedbackFeedView())
        group = mommy.make('core.AssignmentGroup')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)
        student = mommy.make('core.Candidate',
                             assignment_group=group,
                             relatedstudent=mommy.make('core.RelatedStudent'),)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'),)
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset,
                   published_datetime=timezone.now())
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset,
                   published_datetime=timezone.now())
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset,
                   published_datetime=timezone.now())
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset,
                   published_datetime=timezone.now())
        timeline = timeline_builder.add_comments_to_timeline(group, {})
        self.assertEquals(4, len(timeline))

    def test_student_add_comments_to_timeline_examiner_comments_not_visible(self):
        timeline_builder = FeedbackFeedTimelineBuilder(StudentFeedbackFeedView())
        group = mommy.make('core.AssignmentGroup')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)
        student = mommy.make('core.Candidate',
                             assignment_group=group,
                             relatedstudent=mommy.make('core.RelatedStudent'),)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset,
                   published_datetime=timezone.now())
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   feedback_set=feedbackset,
                   published_datetime=timezone.now())
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset,
                   published_datetime=timezone.now())
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   published_datetime=timezone.now())
        timeline = timeline_builder.add_comments_to_timeline(group, {})
        self.assertEquals(2, len(timeline))

    def test_examiner_add_comments_to_timeline(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(examiner_views.ExaminerBaseFeedbackFeedView(request=mockrequest))
        group = mommy.make('core.AssignmentGroup')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)
        student = mommy.make('core.Candidate',
                             assignment_group=group,
                             relatedstudent=mommy.make('core.RelatedStudent'),)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset,
                   published_datetime=timezone.now())
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   feedback_set=feedbackset,
                   published_datetime=timezone.now())
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset,
                   published_datetime=timezone.now())
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   published_datetime=timezone.now())
        timeline = timeline_builder.add_comments_to_timeline(group, {})
        self.assertEquals(4, len(timeline))

    def test_examiner_timeline_builder_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(examiner_views.ExaminerBaseFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'),)
        student = mommy.make('core.Candidate',
                             assignment_group=group,
                             relatedstudent=mommy.make('core.RelatedStudent'),)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=group,
                                  is_last_in_group=None,
                                  created_datetime=assignment.publishing_time)

        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=assignment.first_deadline-timezone.timedelta(days=5))
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset1,
                   published_datetime=assignment.first_deadline-timezone.timedelta(days=4))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=assignment.first_deadline-timezone.timedelta(days=3))

        feedbackset2 = mommy.make('devilry_group.FeedbackSet',
                                  group=group,
                                  created_datetime=timezone.now()-timezone.timedelta(days=10),
                                  deadline_datetime=timezone.now()-timezone.timedelta(days=1))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=timezone.now()-timezone.timedelta(days=4))
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset1,
                   published_datetime=timezone.now()-timezone.timedelta(days=3))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=timezone.now()-timezone.timedelta(days=2))

        timeline_events = []
        last_deadline, timeline = timeline_builder.build_timeline(group, [feedbackset1, feedbackset2])

        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 10)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'comment')
        self.assertEquals(timeline_events[2], 'comment')
        self.assertEquals(timeline_events[3], 'comment')
        self.assertEquals(timeline_events[4], 'deadline_expired')
        self.assertEquals(timeline_events[5], 'deadline_created')
        self.assertEquals(timeline_events[6], 'comment')
        self.assertEquals(timeline_events[7], 'comment')
        self.assertEquals(timeline_events[8], 'comment')
        self.assertEquals(timeline_events[9], 'deadline_expired')

    def test_student_timeline_builder_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(StudentFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'),)
        student = mommy.make('core.Candidate',
                             assignment_group=group,
                             relatedstudent=mommy.make('core.RelatedStudent'),)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=group,
                                  is_last_in_group=None,
                                  created_datetime=assignment.publishing_time)

        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=assignment.first_deadline-timezone.timedelta(days=5))
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset1,
                   published_datetime=assignment.first_deadline-timezone.timedelta(days=4))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=assignment.first_deadline-timezone.timedelta(days=3))

        feedbackset2 = mommy.make('devilry_group.FeedbackSet',
                                  group=group,
                                  created_datetime=timezone.now()-timezone.timedelta(days=10),
                                  deadline_datetime=timezone.now()-timezone.timedelta(days=1))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=timezone.now()-timezone.timedelta(days=4))
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset1,
                   published_datetime=timezone.now()-timezone.timedelta(days=3))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=timezone.now()-timezone.timedelta(days=2))

        timeline_events = []
        last_deadline, timeline = timeline_builder.build_timeline(group, [feedbackset1, feedbackset2])

        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 10)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'comment')
        self.assertEquals(timeline_events[2], 'comment')
        self.assertEquals(timeline_events[3], 'comment')
        self.assertEquals(timeline_events[4], 'deadline_expired')
        self.assertEquals(timeline_events[5], 'deadline_created')
        self.assertEquals(timeline_events[6], 'comment')
        self.assertEquals(timeline_events[7], 'comment')
        self.assertEquals(timeline_events[8], 'comment')
        self.assertEquals(timeline_events[9], 'deadline_expired')

    def test_admin_timeline_builder_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(AdminFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'),)
        student = mommy.make('core.Candidate',
                             assignment_group=group,
                             relatedstudent=mommy.make('core.RelatedStudent'),)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=group,
                                  is_last_in_group=None,
                                  created_datetime=assignment.publishing_time)

        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=assignment.first_deadline-timezone.timedelta(days=5))
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset1,
                   published_datetime=assignment.first_deadline-timezone.timedelta(days=4))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=assignment.first_deadline-timezone.timedelta(days=3))

        feedbackset2 = mommy.make('devilry_group.FeedbackSet',
                                  group=group,
                                  created_datetime=timezone.now()-timezone.timedelta(days=10),
                                  deadline_datetime=timezone.now()-timezone.timedelta(days=1))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=timezone.now()-timezone.timedelta(days=4))
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   feedback_set=feedbackset1,
                   published_datetime=timezone.now()-timezone.timedelta(days=3))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset1,
                   published_datetime=timezone.now()-timezone.timedelta(days=2))

        timeline_events = []
        last_deadline, timeline = timeline_builder.build_timeline(group, [feedbackset1, feedbackset2])

        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 10)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'comment')
        self.assertEquals(timeline_events[2], 'comment')
        self.assertEquals(timeline_events[3], 'comment')
        self.assertEquals(timeline_events[4], 'deadline_expired')
        self.assertEquals(timeline_events[5], 'deadline_created')
        self.assertEquals(timeline_events[6], 'comment')
        self.assertEquals(timeline_events[7], 'comment')
        self.assertEquals(timeline_events[8], 'comment')
        self.assertEquals(timeline_events[9], 'deadline_expired')

    def test_examiner_first_try_published_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(examiner_views.ExaminerBaseFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_published(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset.group, [feedbackset])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 3)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')
        self.assertEquals(timeline_events[2], 'grade')

    def test_student_first_try_published_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(StudentFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_published(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset.group, [feedbackset])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 3)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')
        self.assertEquals(timeline_events[2], 'grade')

    def test_admin_first_try_published_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(AdminFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_published(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset.group, [feedbackset])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')
        self.assertEquals(timeline_events[2], 'grade')

    def test_examiner_new_try_published_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(examiner_views.ExaminerBaseFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset1 = group_mommy.feedbackset_first_attempt_published(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment,
                is_last_in_group=False,)
        feedbackset2 = group_mommy.feedbackset_new_attempt_published(
                created_datetime=timezone.now(),
                deadline_datetime=timezone.now(),
                group=feedbackset1.group,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset1.group, [feedbackset1, feedbackset2])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 6)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')
        self.assertEquals(timeline_events[2], 'grade')
        self.assertEquals(timeline_events[3], 'deadline_created')
        self.assertEquals(timeline_events[4], 'deadline_expired')
        self.assertEquals(timeline_events[5], 'grade')

    def test_student_new_try_published_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(StudentFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset1 = group_mommy.feedbackset_first_attempt_published(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment,
                is_last_in_group=False,)
        feedbackset2 = group_mommy.feedbackset_new_attempt_published(
                created_datetime=timezone.now(),
                deadline_datetime=timezone.now(),
                group=feedbackset1.group,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset1.group, [feedbackset1, feedbackset2])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 6)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')
        self.assertEquals(timeline_events[2], 'grade')
        self.assertEquals(timeline_events[3], 'deadline_created')
        self.assertEquals(timeline_events[4], 'deadline_expired')
        self.assertEquals(timeline_events[5], 'grade')

    def test_admin_new_try_published_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(AdminFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset1 = group_mommy.feedbackset_first_attempt_published(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment,
                is_last_in_group=False,)
        feedbackset2 = group_mommy.feedbackset_new_attempt_published(
                created_datetime=timezone.now(),
                deadline_datetime=timezone.now(),
                group=feedbackset1.group,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset1.group, [feedbackset1, feedbackset2])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 6)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')
        self.assertEquals(timeline_events[2], 'grade')
        self.assertEquals(timeline_events[3], 'deadline_created')
        self.assertEquals(timeline_events[4], 'deadline_expired')
        self.assertEquals(timeline_events[5], 'grade')

    def test_examiner_first_try_unpublished_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(examiner_views.ExaminerBaseFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset.group, [feedbackset])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 2)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')

    def test_student_first_try_unpublished_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(StudentFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset.group, [feedbackset])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 2)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')

    def test_admin_first_try_unpublished_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(AdminFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset.group, [feedbackset])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 2)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')

    def test_examiner_new_try_unpublished_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(examiner_views.ExaminerBaseFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset1 = group_mommy.feedbackset_first_attempt_published(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment,
                is_last_in_group=False,)
        feedbackset2 = group_mommy.feedbackset_new_attempt_unpublished(
                created_datetime=timezone.now(),
                deadline_datetime=timezone.now(),
                group=feedbackset1.group,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset1.group, [feedbackset1, feedbackset2])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 5)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')
        self.assertEquals(timeline_events[2], 'grade')
        self.assertEquals(timeline_events[3], 'deadline_created')
        self.assertEquals(timeline_events[4], 'deadline_expired')

    def test_Student_new_try_unpublished_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(StudentFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset1 = group_mommy.feedbackset_first_attempt_published(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment,
                is_last_in_group=False,)
        feedbackset2 = group_mommy.feedbackset_new_attempt_unpublished(
                created_datetime=timezone.now(),
                deadline_datetime=timezone.now(),
                group=feedbackset1.group,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset1.group, [feedbackset1, feedbackset2])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 5)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')
        self.assertEquals(timeline_events[2], 'grade')
        self.assertEquals(timeline_events[3], 'deadline_created')
        self.assertEquals(timeline_events[4], 'deadline_expired')

    def test_admin_new_try_unpublished_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        timeline_builder = FeedbackFeedTimelineBuilder(AdminFeedbackFeedView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset1 = group_mommy.feedbackset_first_attempt_published(
                created_datetime=assignment.publishing_time,
                group__parentnode=assignment,
                is_last_in_group=False,)
        feedbackset2 = group_mommy.feedbackset_new_attempt_unpublished(
                created_datetime=timezone.now(),
                deadline_datetime=timezone.now(),
                group=feedbackset1.group,
                group__parentnode=assignment)
        last_deadline, timeline = timeline_builder.build_timeline(feedbackset1.group, [feedbackset1, feedbackset2])
        timeline_events = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])

        self.assertEquals(len(timeline_events), 5)
        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'deadline_expired')
        self.assertEquals(timeline_events[2], 'grade')
        self.assertEquals(timeline_events[3], 'deadline_created')
        self.assertEquals(timeline_events[4], 'deadline_expired')

    def test_examiner_discussview_two_feedbacksets_published_with_comments_and_feedback(self):
        examiner = mommy.make(settings.AUTH_USER_MODEL)
        student = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = examiner
        timeline_builder = FeedbackFeedTimelineBuilder(examiner_views.ExaminerDiscussView(request=mockrequest))
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset1 = group_mommy.feedbackset_first_attempt_published(
                grading_published_datetime=timezone.now()-timezone.timedelta(days=10),
                created_datetime=assignment.publishing_time,
                group=group,
                is_last_in_group=None,)

        mommy.make('devilry_group.GroupComment',
                   user=examiner,
                   user_role='examiner',
                   published_datetime=feedbackset1.created_datetime + timezone.timedelta(hours=1),
                   feedback_set=feedbackset1,
                   text='comment1')
        mommy.make('devilry_group.GroupComment',
                   user=student,
                   user_role='student',
                   published_datetime=feedbackset1.created_datetime + timezone.timedelta(hours=2),
                   feedback_set=feedbackset1,
                   text='comment2')
        mommy.make('devilry_group.GroupComment',
                   part_of_grading=True,
                   user=examiner,
                   user_role='examiner',
                   published_datetime=feedbackset1.grading_published_datetime-timezone.timedelta(milliseconds=2),
                   feedback_set=feedbackset1,
                   text='feedbackcomment1')
        mommy.make('devilry_group.GroupComment',
                   part_of_grading=True,
                   user=examiner,
                   user_role='examiner',
                   published_datetime=feedbackset1.grading_published_datetime-timezone.timedelta(milliseconds=1),
                   feedback_set=feedbackset1,
                   text='feedbackcomment2')

        now = timezone.now()
        feedbackset2 = group_mommy.feedbackset_new_attempt_published(
            created_datetime=now-timezone.timedelta(days=8),
            deadline_datetime=now-timezone.timedelta(days=2),
            grading_published_datetime=now-timezone.timedelta(days=1),
            group=group,
            is_last_in_group=True,)

        mommy.make('devilry_group.GroupComment',
                   user=examiner,
                   user_role='examiner',
                   published_datetime=feedbackset2.created_datetime + timezone.timedelta(hours=1),
                   feedback_set=feedbackset2,
                   text='comment3')
        mommy.make('devilry_group.GroupComment',
                   user=student,
                   user_role='student',
                   published_datetime=feedbackset2.created_datetime + timezone.timedelta(hours=2),
                   feedback_set=feedbackset2,
                   text='comment4')
        mommy.make('devilry_group.GroupComment',
                   part_of_grading=True,
                   published_datetime=feedbackset2.grading_published_datetime-timezone.timedelta(milliseconds=2),
                   user=examiner,
                   user_role='examiner',
                   feedback_set=feedbackset2,
                   text='feedbackcomment3')
        mommy.make('devilry_group.GroupComment',
                   part_of_grading=True,
                   published_datetime=feedbackset2.grading_published_datetime-timezone.timedelta(milliseconds=1),
                   user=examiner,
                   user_role='examiner',
                   feedback_set=feedbackset2,
                   text='feedbackcomment4')

        last_deadline, timeline = timeline_builder.build_timeline(group, [feedbackset1, feedbackset2])
        timeline_events = []
        timeline_objects = []
        for timestamp, eventlist in timeline.items():
            timeline_events.append(eventlist[0]['type'])
            timeline_objects.append(eventlist[0]['obj'])

        self.assertEquals(len(timeline_events), 14)

        self.assertEquals(timeline_events[0], 'deadline_created')
        self.assertEquals(timeline_events[1], 'comment')
        self.assertEquals(timeline_objects[1].text, 'comment1')
        self.assertEquals(timeline_events[2], 'comment')
        self.assertEquals(timeline_objects[2].text, 'comment2')
        self.assertEquals(timeline_events[3], 'deadline_expired')
        self.assertEquals(timeline_events[4], 'comment')
        self.assertEquals(timeline_objects[4].text, 'feedbackcomment1')
        self.assertEquals(timeline_events[5], 'comment')
        self.assertEquals(timeline_objects[5].text, 'feedbackcomment2')
        self.assertEquals(timeline_events[6], 'grade')

        self.assertEquals(timeline_events[7], 'deadline_created')
        self.assertEquals(timeline_events[8], 'comment')
        self.assertEquals(timeline_objects[8].text, 'comment3')
        self.assertEquals(timeline_events[9], 'comment')
        self.assertEquals(timeline_objects[9].text, 'comment4')
        self.assertEquals(timeline_events[10], 'deadline_expired')
        self.assertEquals(timeline_events[11], 'comment')
        self.assertEquals(timeline_objects[11].text, 'feedbackcomment3')
        self.assertEquals(timeline_events[12], 'comment')
        self.assertEquals(timeline_objects[12].text, 'feedbackcomment4')
        self.assertEquals(timeline_events[13], 'grade')
