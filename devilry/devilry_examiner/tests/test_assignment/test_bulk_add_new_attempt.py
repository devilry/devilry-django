# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django import http
from django import test
from django.contrib import messages
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_dbcache import customsql
from devilry.devilry_dbcache import models as cache_models
from devilry.devilry_examiner.views.assignment.bulkoperations import bulk_add_new_attempt
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group import models as group_models
from devilry.project.common import settings


class TestBulkAddNewAttempt(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_add_new_attempt.BulkAddNewAttemptListView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def test_title(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user)
        self.assertIn(
            'Bulk add new attempt',
            mockresponse.selector.one('title').alltext_normalized)

    def test_raises_404_with_less_than_two_groups(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        with self.assertRaises(http.Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user)

    def test_success_message(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        mommy.make('core.Candidate', assignment_group=testgroup1,
                   relatedstudent__user__fullname='Candidate1',
                   relatedstudent__user__shortname='candidate1')
        mommy.make('core.Candidate', assignment_group=testgroup2,
                   relatedstudent__user__fullname='Candidate2',
                   relatedstudent__user__shortname='candidate2')
        # create FeedbackSets for the AssignmentGroups
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        new_deadline = timezone.now() + timezone.timedelta(days=10)
        messagemock = mock.MagicMock()
        self.mock_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'new_deadline': new_deadline.strftime('%Y-%m-%d %H:%M'),
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup1.id]
                }
            },
            messagesmock=messagemock
        )
        messagemock.add.assert_called_once_with(
            messages.SUCCESS,
            'Bulk added new attempt for {}'.format(testgroup1.get_anonymous_displayname(assignment=testassignment)),
            '')

    def test_three_groups_on_assignment_unpublished(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user)
        self.assertEquals(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_three_groups_on_assignment_published(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user)
        self.assertEquals(
            3,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_post_new_feedbackset_deadlines(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)
        new_deadline = timezone.now() + timezone.timedelta(days=10)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'feedback_comment_text': 'new attempt given',
                    'new_deadline': new_deadline,
                    'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id]
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertEquals(6, feedbacksets.count())
        feedbacksets = feedbacksets.filter(feedbackset_type=group_models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        self.assertEquals(3, feedbacksets.count())
        self.assertIn(new_deadline, [fb.deadline_datetime for fb in feedbacksets])

    def test_post_new_attempt_for_groups(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)
        new_deadline = timezone.now() + timezone.timedelta(days=10)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'feedback_comment_text': 'new attempt given',
                    'new_deadline': new_deadline.strftime('%Y-%m-%d %H:%M'),
                    'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id]
                }
            })

        self.assertEquals(6, group_models.FeedbackSet.objects.count())

        cached_data_group1 = cache_models.AssignmentGroupCachedData.objects.get(group_id=testgroup1.id)
        cached_data_group2 = cache_models.AssignmentGroupCachedData.objects.get(group_id=testgroup2.id)
        cached_data_group3 = cache_models.AssignmentGroupCachedData.objects.get(group_id=testgroup3.id)
        self.assertNotEquals(cached_data_group1.last_published_feedbackset, cached_data_group1.last_feedbackset)
        self.assertNotEquals(cached_data_group2.last_published_feedbackset, cached_data_group2.last_feedbackset)
        self.assertNotEquals(cached_data_group3.last_published_feedbackset, cached_data_group3.last_feedbackset)

        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals(3, group_comments.count())
        self.assertIn('new attempt given', [comment.text for comment in group_comments])

    def test_post_new_attempt_for_groups_not_yet_corrected(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        new_deadline = timezone.now() + timezone.timedelta(days=10)
        self.mock_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'feedback_comment_text': 'new attempt given',
                    'new_deadline': new_deadline.strftime('%Y-%m-%d %H:%M'),
                    'selected_items': [testgroup1.id, testgroup2.id]
                }
            })

        self.assertEquals(2, group_models.FeedbackSet.objects.count())

        cached_data_group1 = cache_models.AssignmentGroupCachedData.objects.get(group_id=testgroup1.id)
        cached_data_group2 = cache_models.AssignmentGroupCachedData.objects.get(group_id=testgroup2.id)
        self.assertNotEquals(cached_data_group1.last_published_feedbackset, cached_data_group1.last_feedbackset)
        self.assertNotEquals(cached_data_group2.last_published_feedbackset, cached_data_group2.last_feedbackset)

        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals(0, group_comments.count())
