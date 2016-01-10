from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from devilry.devilry_group.views.feedbackfeed_admin import AdminFeedbackFeedView
from devilry.devilry_group.views.feedbackfeed_examiner import ExaminerFeedbackFeedView
from devilry.devilry_group.views.feedbackfeed_student import StudentFeedbackFeedView
from devilry.devilry_group.views.feedbackfeed_timeline_builder import FeedbackFeedTimelineBuilder


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
        timeline_builder = FeedbackFeedTimelineBuilder(ExaminerFeedbackFeedView())
        timeline = timeline_builder.build_timeline(feedbackset.group, [feedbackset])
        self.assertEquals(timeline[0], feedbackset.group.assignment.first_deadline)

    def test_examiner_timelinebuilder_two_feedbacksets_last_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group__parentnode=assignment)
        feedbackset2 = mommy.make('devilry_group.FeedbackSet',
                                  group=feedbackset1.group,
                                  deadline_datetime=timezone.now())
        timeline_builder = FeedbackFeedTimelineBuilder(ExaminerFeedbackFeedView())
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
                                  group__parentnode=assignment)
        feedbackset2 = mommy.make('devilry_group.FeedbackSet',
                                  group=feedbackset1.group,
                                  deadline_datetime=timezone.now())
        timeline_builder = FeedbackFeedTimelineBuilder(AdminFeedbackFeedView())
        timeline = timeline_builder.build_timeline(feedbackset1.group, [feedbackset1, feedbackset2])
        self.assertEquals(timeline[0], feedbackset2.deadline_datetime)


    def test_get_feedbacksets_for_group(self):
        timelinebuilder = FeedbackFeedTimelineBuilder(None)
        assignment_group = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet', group=assignment_group)
        mommy.make('devilry_group.FeedbackSet', group=assignment_group)
        mommy.make('devilry_group.FeedbackSet', group=assignment_group)
        mommy.make('devilry_group.FeedbackSet', group=assignment_group)
        mommy.make('devilry_group.FeedbackSet', group=assignment_group)

        self.assertEquals(5, len(timelinebuilder.get_feedbacksets_for_group(assignment_group)))
