# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django import test
from django.conf import settings
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_dbcache.models import AssignmentGroupCachedData
from devilry.devilry_deadlinemanagement.views import manage_deadline_view
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.utils import datetimeutils


class AdminTestMixin(object):

    def _get_mock_instance(self):
        mock_instance = mock.MagicMock()
        mock_instance.get_devilryrole_type.return_value = 'admin'
        return mock_instance

    def _get_mock_app(self, user=None):
        mock_app = mock.MagicMock()
        mock_app.get_devilryrole.return_value = 'admin'
        mock_app.get_accessible_group_queryset.return_value = core_models.AssignmentGroup.objects \
            .filter_user_is_admin(user=user)
        return mock_app


class TestPostManageDeadlineAdminView(AdminTestMixin, test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_post_from_previous_view_selected_groups_are_hidden(self):
        # By adding the post_type_received_data to the key, we are simulating that the
        # post comes from a different view.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'move-deadline'
            },
            requestkwargs={
                'data': {
                    'post_type_received_data': '',
                    'selected_items': [testgroup1.id, testgroup2.id]
                }
            }
        )
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_1').__str__())
        self.assertIn('value="{}"'.format(testgroup1.id),
                      mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('value="{}"'.format(testgroup2.id),
                      mockresponse.selector.one('#id_selected_items_1').__str__())

    def test_post_new_attempt(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        self.mock_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'new-attempt'
            },
            requestkwargs={
                'data': {
                    'new_deadline': new_deadline,
                    'comment_text': 'You have been given a new attempt.',
                    'selected_items': [testgroup1.id, testgroup2.id]
                }
            }
        )
        self.assertEquals(4, group_models.FeedbackSet.objects.count())
        self.assertEquals(2, group_models.GroupComment.objects.count())
        group_comments = group_models.GroupComment.objects.all()
        last_feedbackset_group1 = AssignmentGroupCachedData.objects.get(group_id=testgroup1.id).last_feedbackset
        last_feedbackset_group2 = AssignmentGroupCachedData.objects.get(group_id=testgroup2.id).last_feedbackset
        self.assertEquals(last_feedbackset_group1.deadline_datetime, new_deadline)
        self.assertEquals(last_feedbackset_group2.deadline_datetime, new_deadline)
        self.assertEquals('You have been given a new attempt.', group_comments[0].text)
        self.assertEquals('You have been given a new attempt.', group_comments[1].text)

    def test_post_move_deadline_does_not_move_assignment_first_deadline(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        self.mock_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'move-deadline'
            },
            requestkwargs={
                'data': {
                    'new_deadline': new_deadline,
                    'comment_text': 'You have been given a new attempt.',
                    'selected_items': [testgroup1.id, testgroup2.id]
                }
            }
        )
        last_feedbackset_group1 = AssignmentGroupCachedData.objects.get(group_id=testgroup1.id).last_feedbackset
        last_feedbackset_group2 = AssignmentGroupCachedData.objects.get(group_id=testgroup2.id).last_feedbackset
        self.assertEquals(2, group_models.FeedbackSet.objects.count())
        self.assertNotEquals(testassignment.first_deadline, last_feedbackset_group1.deadline_datetime)
        self.assertNotEquals(testassignment.first_deadline, last_feedbackset_group2.deadline_datetime)


class TestGetManageDeadlineAdminView(AdminTestMixin, test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineSingleGroupView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_from_previous_view_selected_group_is_hidden(self):
        # By adding the post_type_received_data to the key, we are simulating that the
        # post comes from a different view.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'group_id': testgroup1.id
            }
        )
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('value="{}"'.format(testgroup1.id),
                      mockresponse.selector.one('#id_selected_items_0').__str__())


# class TestManageDeadlineViewAllGroups(AdminTestMixin, test.TestCase, cradmin_testhelpers.TestCaseMixin):
#     viewclass = manage_deadline_view.ManageDeadlineAllGroupsView
#
#     def setUp(self):
#         AssignmentGroupDbCacheCustomSql().initialize()
#
#     def test_post_move_deadline_moves_assignment_first_deadline(self):
#         testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
#         group_mommy.feedbackset_first_attempt_published(
#             group=testgroup1,
#             deadline_datetime=testassignment.first_deadline)
#         testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
#         group_mommy.feedbackset_first_attempt_published(
#             group=testgroup2,
#             deadline_datetime=testassignment.first_deadline)
#         testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
#         new_deadline = timezone.now() + timezone.timedelta(days=3)
#         new_deadline = new_deadline.replace(second=0, microsecond=0)
#         self.mock_postrequest(
#             cradmin_role=testassignment,
#             cradmin_instance=self._get_mock_instance(),
#             cradmin_app=self._get_mock_app(user=testuser),
#             requestuser=testuser,
#             viewkwargs={
#                 'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
#                 'handle_deadline': 'move-deadline'
#             },
#             requestkwargs={
#                 'data': {
#                     'new_deadline': new_deadline,
#                     'comment_text': 'You have been given a new attempt.',
#                     'selected_items': [testgroup1.id, testgroup2.id]
#                 }
#             }
#         )
#         last_feedbackset_group1 = AssignmentGroupCachedData.objects.get(group_id=testgroup1.id).last_feedbackset
#         last_feedbackset_group2 = AssignmentGroupCachedData.objects.get(group_id=testgroup2.id).last_feedbackset
#         assignment = core_models.Assignment.objects.get(id=testassignment.id)
#         self.assertEquals(2, group_models.FeedbackSet.objects.count())
#         self.assertEquals(2, group_models.GroupComment.objects.count())
#         self.assertEquals(assignment.first_deadline, new_deadline)
#         self.assertEquals(assignment.first_deadline, last_feedbackset_group1.deadline_datetime)
#         self.assertEquals(assignment.first_deadline, last_feedbackset_group2.deadline_datetime)
#
#     def test_post_move_deadline_feedbackset_first_attempt_deadline_ahead_of_first_deadline(self):
#         testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
#         group_mommy.feedbackset_first_attempt_published(
#             group=testgroup1,
#             deadline_datetime=testassignment.first_deadline)
#         testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
#         group_mommy.feedbackset_first_attempt_published(
#             group=testgroup2,
#             deadline_datetime=timezone.now())
#         testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
#         new_deadline = timezone.now() + timezone.timedelta(days=3)
#         new_deadline = new_deadline.replace(second=0, microsecond=0)
#         self.mock_postrequest(
#             cradmin_role=testassignment,
#             cradmin_instance=self._get_mock_instance(),
#             cradmin_app=self._get_mock_app(user=testuser),
#             requestuser=testuser,
#             viewkwargs={
#                 'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
#                 'handle_deadline': 'move-deadline'
#             },
#             requestkwargs={
#                 'data': {
#                     'new_deadline': new_deadline,
#                     'comment_text': 'You have been given a new attempt.',
#                     'selected_items': [testgroup1.id, testgroup2.id]
#                 }
#             }
#         )
#         last_feedback_set_group1 = AssignmentGroupCachedData.objects.get(group_id=testgroup1.id).last_feedbackset
#         last_feedback_set_group2 = AssignmentGroupCachedData.objects.get(group_id=testgroup2.id).last_feedbackset
#         assignment = core_models.Assignment.objects.get(id=testassignment.id)
#         self.assertNotEquals(assignment.first_deadline, new_deadline)
#         self.assertEquals(assignment.first_deadline, testassignment.first_deadline)
#         self.assertNotEquals(last_feedback_set_group1.deadline_datetime, assignment.first_deadline)
#         self.assertNotEquals(last_feedback_set_group2.deadline_datetime, assignment.first_deadline)
#         self.assertEquals(last_feedback_set_group1.deadline_datetime, new_deadline)
#         self.assertEquals(last_feedback_set_group2.deadline_datetime, new_deadline)
#
#     def test_first_deadline_not_moved_if_current_deadline_is_not_first_deadline(self):
#         testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
#         current_deadline = timezone.now()
#         group_mommy.feedbackset_first_attempt_published(
#             group=testgroup1,
#             deadline_datetime=testassignment.first_deadline)
#         testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
#         group_mommy.feedbackset_first_attempt_published(
#             group=testgroup2,
#             deadline_datetime=testassignment.first_deadline)
#         testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
#         new_deadline = timezone.now() + timezone.timedelta(days=3)
#         new_deadline = new_deadline.replace(second=0, microsecond=0)
#         self.mock_postrequest(
#             cradmin_role=testassignment,
#             cradmin_instance=self._get_mock_instance(),
#             cradmin_app=self._get_mock_app(user=testuser),
#             requestuser=testuser,
#             viewkwargs={
#                 'deadline': datetimeutils.datetime_to_string(current_deadline),
#                 'handle_deadline': 'move-deadline'
#             },
#             requestkwargs={
#                 'data': {
#                     'new_deadline': new_deadline,
#                     'comment_text': 'You have been given a new attempt.',
#                     'selected_items': [testgroup1.id, testgroup2.id]
#                 }
#             }
#         )
#         assignment = core_models.Assignment.objects.get(id=testassignment.id)
#         self.assertNotEquals(assignment.first_deadline, new_deadline)
#         self.assertEquals(assignment.first_deadline, testassignment.first_deadline)
