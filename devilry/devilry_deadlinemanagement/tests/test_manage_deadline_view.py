# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django import http
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy
from django import forms
from django_cradmin.crispylayouts import DefaultSubmitBlock
from django_cradmin.crispylayouts import PrimarySubmitBlock
from django import test
from django.conf import settings

from model_mommy import mommy
import mock

from django_cradmin import cradmin_testhelpers
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget
from django_cradmin.viewhelpers import formbase
from crispy_forms import layout

from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter
from devilry.devilry_deadlinemanagement.views import viewutils
from devilry.devilry_group import models as group_models
from devilry.utils import datetimeutils
from devilry.devilry_deadlinemanagement.views import manage_deadline_view
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.apps.core import models as core_models
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_dbcache.models import AssignmentGroupCachedData


class TestPostManageDeadlineExaminerView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    Tests posting data from another view, and the actual posting in this view.
    """
    viewclass = manage_deadline_view.ManageDeadlineView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __get_mock_app(self, user=None):
        mock_app = mock.MagicMock()
        mock_app.get_devilryrole.return_value = 'examiner'
        mock_app.get_accessible_group_queryset.return_value = core_models.AssignmentGroup.objects\
            .filter_examiner_has_access(user=user)
        return mock_app

    def test_post_from_previous_view_selected_groups_are_hidden(self):
        # By adding the post_type_received_data to the key, we are simulating that the
        # post comes from a different view.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser,
            requestattributes={'devilryrole_type': 'examiner'},
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline)
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
        self.assertIn('value="{}"'.format(testgroup1.id), mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('value="{}"'.format(testgroup2.id), mockresponse.selector.one('#id_selected_items_1').__str__())

    def test_post_new_attempt(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        self.mock_postrequest(
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser,
            requestattributes={'devilryrole_type': 'examiner'},
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline)
            },
            requestkwargs={
                'data': {
                    'new_attempt': '',
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

    def test_post_move_deadline_examiner_moved_feedbackset_deadline_not_assignment_first_deadline(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        self.mock_postrequest(
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser,
            requestattributes={'devilryrole_type': 'examiner'},
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline)
            },
            requestkwargs={
                'data': {
                    'move_deadline': '',
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
        self.assertEquals(last_feedbackset_group1.deadline_datetime, new_deadline)
        self.assertEquals(last_feedbackset_group2.deadline_datetime, new_deadline)


class TestGetManageDeadlineExaminerView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __get_mock_app(self, user=None):
        mock_app = mock.MagicMock()
        mock_app.get_devilryrole.return_value = 'examiner'
        mock_app.get_accessible_group_queryset.return_value = core_models.AssignmentGroup.objects \
            .filter_examiner_has_access(user=user)
        return mock_app

    def test_get_from_previous_view_selected_group_is_hidden(self):
        # By adding the post_type_received_data to the key, we are simulating that the
        # post comes from a different view.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser,
            requestattributes={'devilryrole_type': 'examiner'},
            viewkwargs={
                # 'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'group_id': testgroup1.id
            }
        )
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('value="{}"'.format(testgroup1.id),
                      mockresponse.selector.one('#id_selected_items_0').__str__())


class TestPostManageDeadlineAdminView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __get_mock_app(self, user=None):
        mock_app = mock.MagicMock()
        mock_app.get_devilryrole.return_value = 'admin'
        mock_app.get_accessible_group_queryset.return_value = core_models.AssignmentGroup.objects\
            .filter_user_is_admin(user=user)
        return mock_app

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
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser,
            requestattributes={'devilryrole_type': 'admin'},
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline)
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
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser,
            requestattributes={'devilryrole_type': 'admin'},
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline)
            },
            requestkwargs={
                'data': {
                    'new_attempt': '',
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

    def test_post_move_deadline_examiner_moved_feedbackset_deadline_not_assignment_first_deadline(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        self.mock_postrequest(
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser,
            requestattributes={'devilryrole_type': 'admin'},
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline)
            },
            requestkwargs={
                'data': {
                    'move_deadline': '',
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
        self.assertEquals(last_feedbackset_group1.deadline_datetime, new_deadline)
        self.assertEquals(last_feedbackset_group2.deadline_datetime, new_deadline)

    # def test_post_move_deadline_superuser_moves_assignment_first_deadline(self):
    #     testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
    #     testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
    #     group_mommy.feedbackset_first_attempt_published(group=testgroup1, grading_points=0)
    #     testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
    #     group_mommy.feedbackset_first_attempt_published(group=testgroup2, grading_points=0)
    #     testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
    #
    #     # clean new deadline as this is what Assignment does.
    #     new_deadline = timezone.now() + timezone.timedelta(days=3)
    #     new_deadline = new_deadline.replace(second=0, microsecond=0)
    #     self.mock_postrequest(
    #         cradmin_role=testassignment,
    #         cradmin_app=self.__get_mock_app(user=testuser),
    #         requestuser=testuser,
    #         requestattributes={'devilryrole_type': 'admin'},
    #         viewkwargs={
    #             'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline)
    #         },
    #         requestkwargs={
    #             'data': {
    #                 'move_deadline': '',
    #                 'new_deadline': new_deadline,
    #                 'comment_text': 'You have been given a new attempt.',
    #                 'selected_items': [testgroup1.id, testgroup2.id]
    #             }
    #         }
    #     )
    #     assignment = core_models.Assignment.objects.get(id=testassignment.id)
    #     feedbacksets = group_models.FeedbackSet.objects.all()
    #     self.assertEquals(assignment.first_deadline, new_deadline)
    #     self.assertEquals(feedbacksets[0].deadline_datetime, assignment.first_deadline)
    #     self.assertEquals(feedbacksets[1].deadline_datetime, assignment.first_deadline)


class TestGetManageDeadlineAdminView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __get_mock_app(self, user=None):
        mock_app = mock.MagicMock()
        mock_app.get_devilryrole.return_value = 'admin'
        mock_app.get_accessible_group_queryset.return_value = core_models.AssignmentGroup.objects\
            .filter_user_is_admin(user=user)
        return mock_app

    def test_get_from_previous_view_selected_group_is_hidden(self):
        # By adding the post_type_received_data to the key, we are simulating that the
        # post comes from a different view.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser,
            requestattributes={'devilryrole_type': 'admin'},
            viewkwargs={
                # 'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'group_id': testgroup1.id
            }
        )
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('value="{}"'.format(testgroup1.id),
                      mockresponse.selector.one('#id_selected_items_0').__str__())