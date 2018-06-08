# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

import mock
from django import http
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
from devilry.utils.datetimeutils import from_isoformat_noseconds, isoformat_withseconds, isoformat_noseconds


class ExaminerTestCaseMixin(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineAllGroupsView
    handle_deadline = 'new-attempt'

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def _get_mock_instance(self, assignment):
        mock_instance = mock.MagicMock()
        mock_instance.get_devilryrole_type.return_value = 'examiner'
        mock_instance.assignment = assignment
        return mock_instance

    def _get_mock_app(self, user=None):
        mock_app = mock.MagicMock()
        mock_app.get_devilryrole.return_value = 'examiner'
        mock_app.get_accessible_group_queryset.return_value = core_models.AssignmentGroup.objects\
            .filter_examiner_has_access(user=user)
        return mock_app


class TestManageDeadlineNewAttemptAllGroupsView(ExaminerTestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineAllGroupsView
    handle_deadline = 'new-attempt'

    def test_info_box_not_showing_when_zero_groups_were_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-deadline-management-info-box'))

    def test_info_box_showing_when_one_group_was_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-deadline-management-info-box'))
        self.assertIn(
            '1 group(s) excluded',
            mockresponse.selector.one('.devilry-deadline-management-info-box').alltext_normalized)

    def test_info_box_showing_when_multiple_groups_were_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-deadline-management-info-box'))
        self.assertIn(
            '2 group(s) excluded',
            mockresponse.selector.one('.devilry-deadline-management-info-box').alltext_normalized)

    def test_all_groups_added_to_form_hidden(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup3)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup4)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_1').__str__())
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_2').__str__())
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_3').__str__())
        self.assertIn('value="{}"'.format(testgroup1.id), mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('value="{}"'.format(testgroup2.id), mockresponse.selector.one('#id_selected_items_1').__str__())
        self.assertIn('value="{}"'.format(testgroup3.id), mockresponse.selector.one('#id_selected_items_2').__str__())
        self.assertIn('value="{}"'.format(testgroup4.id), mockresponse.selector.one('#id_selected_items_3').__str__())

    def test_all_only_one_group_added_to_form_hidden(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('value="{}"'.format(testgroup1.id), mockresponse.selector.one('#id_selected_items_0').__str__())

    def test_post_only_groups_added_as_form_hidden_input(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            },
            requestkwargs={
                'data': {
                    'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                    'comment_text': 'You have been given a new attempt.',
                    'selected_items': [testgroup1.id]
                }
            }
        )
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertEqual(3, feedbacksets.count())
        group1 = core_models.AssignmentGroup.objects.get(id=testgroup1.id)
        group2 = core_models.AssignmentGroup.objects.get(id=testgroup2.id)
        self.assertEqual(new_deadline, group1.cached_data.last_feedbackset.deadline_datetime)
        self.assertNotEqual(new_deadline, group2.cached_data.last_feedbackset.deadline_datetime)

    def test_post_groups_unpublished_raises_error(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        with self.assertRaises(http.Http404):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                cradmin_instance=self._get_mock_instance(testassignment),
                cradmin_app=self._get_mock_app(user=testuser),
                requestuser=testuser,
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                    'handle_deadline': self.handle_deadline
                },
                requestkwargs={
                    'data': {
                        'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                        'comment_text': 'You have been given a new attempt.',
                        'selected_items': [testgroup1.id, testgroup2.id]
                    }
                }
            )
        self.assertEqual(2, group_models.FeedbackSet.objects.count())


class TestManageDeadlineMoveDeadlineAllGroupsView(ExaminerTestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineAllGroupsView
    handle_deadline = 'move-deadline'

    def test_info_box_not_showing_when_zero_groups_were_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-deadline-management-info-box'))

    def test_info_box_showing_when_one_group_was_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-deadline-management-info-box'))
        self.assertIn(
            '1 group(s) excluded',
            mockresponse.selector.one('.devilry-deadline-management-info-box').alltext_normalized)

    def test_info_box_showing_when_multiple_groups_were_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        group_mommy.feedbackset_first_attempt_published(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-deadline-management-info-box'))
        self.assertIn(
            '2 group(s) excluded',
            mockresponse.selector.one('.devilry-deadline-management-info-box').alltext_normalized)

    def test_all_groups_added_to_form_hidden(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup3)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup4)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_1').__str__())
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_2').__str__())
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_3').__str__())
        self.assertIn('value="{}"'.format(testgroup1.id), mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('value="{}"'.format(testgroup2.id), mockresponse.selector.one('#id_selected_items_1').__str__())
        self.assertIn('value="{}"'.format(testgroup3.id), mockresponse.selector.one('#id_selected_items_2').__str__())
        self.assertIn('value="{}"'.format(testgroup4.id), mockresponse.selector.one('#id_selected_items_3').__str__())

    def test_all_only_one_group_added_to_form_hidden(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('value="{}"'.format(testgroup1.id), mockresponse.selector.one('#id_selected_items_0').__str__())

    def test_post_only_groups_added_as_form_hidden_input(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            },
            requestkwargs={
                'data': {
                    'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                    'comment_text': 'Deadline has been moved',
                    'selected_items': [testgroup1.id]
                }
            }
        )
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertEqual(2, feedbacksets.count())
        group1 = core_models.AssignmentGroup.objects.get(id=testgroup1.id)
        group2 = core_models.AssignmentGroup.objects.get(id=testgroup2.id)
        self.assertEqual(group1.cached_data.last_feedbackset, group1.cached_data.first_feedbackset)
        self.assertEqual(new_deadline, group1.cached_data.last_feedbackset.deadline_datetime)
        self.assertNotEqual(new_deadline, group2.cached_data.last_feedbackset.deadline_datetime)

    def test_post_groups_published_raises_error(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        with self.assertRaises(http.Http404):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                cradmin_instance=self._get_mock_instance(testassignment),
                cradmin_app=self._get_mock_app(user=testuser),
                requestuser=testuser,
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                    'handle_deadline': self.handle_deadline
                },
                requestkwargs={
                    'data': {
                        'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                        'comment_text': 'Deadline has been moved',
                        'selected_items': [testgroup1.id, testgroup2.id]
                    }
                }
            )
        self.assertEqual(2, group_models.FeedbackSet.objects.count())

    def test_post_only_moves_deadline_for_feedbacksets_that_are_last(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        last_deadline = timezone.now()
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        group_mommy.feedbackset_new_attempt_unpublished(group=testgroup1, deadline_datetime=last_deadline)
        group_mommy.feedbackset_new_attempt_unpublished(group=testgroup2, deadline_datetime=last_deadline)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(last_deadline),
                'handle_deadline': self.handle_deadline
            },
            requestkwargs={
                'data': {
                    'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                    'comment_text': 'Deadline has been moved',
                    'selected_items': [testgroup1.id, testgroup2.id]
                }
            }
        )
        self.assertEqual(4, group_models.FeedbackSet.objects.count())
        cached_data_group1 = core_models.AssignmentGroup.objects.get(id=testgroup1.id).cached_data
        cached_data_group2 = core_models.AssignmentGroup.objects.get(id=testgroup2.id).cached_data
        self.assertEqual(cached_data_group1.first_feedbackset.deadline_datetime, testassignment.first_deadline)
        self.assertEqual(cached_data_group2.first_feedbackset.deadline_datetime, testassignment.first_deadline)
        self.assertEqual(cached_data_group2.last_feedbackset.deadline_datetime, new_deadline)
        self.assertEqual(cached_data_group2.last_feedbackset.deadline_datetime, new_deadline)
        self.assertEqual(cached_data_group2.last_feedbackset.last_updated_by, testuser)
        self.assertEqual(cached_data_group2.last_feedbackset.last_updated_by, testuser)

    def test_post_only_moves_deadline_for_feedbacksets_that_are_last_first_attempt_and_new_attempt(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        last_deadline = timezone.now().replace(microsecond=0)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1, deadline_datetime=last_deadline)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        group_mommy.feedbackset_new_attempt_unpublished(group=testgroup2, deadline_datetime=last_deadline)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(last_deadline),
                'handle_deadline': self.handle_deadline
            },
            requestkwargs={
                'data': {
                    'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                    'comment_text': 'Deadline has been moved',
                    'selected_items': [testgroup1.id, testgroup2.id]
                }
            }
        )
        self.assertEqual(3, group_models.FeedbackSet.objects.count())
        cached_data_group1 = core_models.AssignmentGroup.objects.get(id=testgroup1.id).cached_data
        cached_data_group2 = core_models.AssignmentGroup.objects.get(id=testgroup2.id).cached_data
        self.assertEqual(cached_data_group1.last_feedbackset.deadline_datetime, new_deadline)
        self.assertEqual(cached_data_group1.last_feedbackset.last_updated_by, testuser)
        self.assertEqual(cached_data_group2.first_feedbackset.deadline_datetime, testassignment.first_deadline)


class TestManageDeadlineNewAttemptFromPreviousView(ExaminerTestCaseMixin):
    """
    Tests posting data from another view, and the actual posting in this view.
    """
    viewclass = manage_deadline_view.ManageDeadlineFromPreviousView
    handle_deadline = 'new-attempt'

    def test_info_box_not_showing_when_zero_group_were_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-deadline-management-info-box'))

    def test_info_box_showing_when_one_group_was_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-deadline-management-info-box'))
        self.assertIn(
            '1 group(s) excluded',
            mockresponse.selector.one('.devilry-deadline-management-info-box').alltext_normalized)

    def test_info_box_showing_when_multiple_groups_were_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-deadline-management-info-box'))
        self.assertIn(
            '2 group(s) excluded',
            mockresponse.selector.one('.devilry-deadline-management-info-box').alltext_normalized)

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
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
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
        new_deadline = new_deadline.replace(microsecond=0)
        self.mock_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': 'new-attempt'
            },
            requestkwargs={
                'data': {
                    'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                    'comment_text': 'You have been given a new attempt.',
                    'selected_items': [testgroup1.id, testgroup2.id]
                }
            }
        )
        self.assertEqual(4, group_models.FeedbackSet.objects.count())
        self.assertEqual(2, group_models.GroupComment.objects.count())
        group_comments = group_models.GroupComment.objects.all()
        last_feedbackset_group1 = AssignmentGroupCachedData.objects.get(group_id=testgroup1.id).last_feedbackset
        last_feedbackset_group2 = AssignmentGroupCachedData.objects.get(group_id=testgroup2.id).last_feedbackset
        self.assertEqual(last_feedbackset_group1.deadline_datetime, new_deadline)
        self.assertEqual(last_feedbackset_group2.deadline_datetime, new_deadline)
        self.assertEqual(last_feedbackset_group1.last_updated_by, testuser)
        self.assertEqual(last_feedbackset_group2.last_updated_by, testuser)
        self.assertEqual('You have been given a new attempt.', group_comments[0].text)
        self.assertEqual('You have been given a new attempt.', group_comments[1].text)

    def test_post_groups_published_raises_error(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        with self.assertRaises(http.Http404):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                cradmin_instance=self._get_mock_instance(testassignment),
                cradmin_app=self._get_mock_app(user=testuser),
                requestuser=testuser,
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                    'handle_deadline': self.handle_deadline
                },
                requestkwargs={
                    'data': {
                        'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                        'comment_text': 'You have been given a new attempt.',
                        'selected_items': [testgroup1.id, testgroup2.id]
                    }
                }
            )
        self.assertEqual(2, group_models.FeedbackSet.objects.count())


class TestManageDeadlineMoveDeadlineFromPreviousView(ExaminerTestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineFromPreviousView
    handle_deadline = 'move-deadline'

    def test_info_box_not_showing_when_zero_group_were_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-deadline-management-info-box'))

    def test_info_box_showing_when_one_group_was_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-deadline-management-info-box'))
        self.assertIn(
            '1 group(s) excluded',
            mockresponse.selector.one('.devilry-deadline-management-info-box').alltext_normalized)

    def test_info_box_showing_when_multiple_groups_were_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        group_mommy.feedbackset_first_attempt_published(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-deadline-management-info-box'))
        self.assertIn(
            '2 group(s) excluded',
            mockresponse.selector.one('.devilry-deadline-management-info-box').alltext_normalized)

    def test_post_from_previous_view_selected_groups_are_hidden(self):
        # By adding the post_type_received_data to the key, we are simulating that the
        # post comes from a different view.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline
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
        new_deadline = new_deadline.replace(microsecond=0)
        self.mock_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': 'new-attempt'
            },
            requestkwargs={
                'data': {
                    'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                    'comment_text': 'You have been given a new attempt.',
                    'selected_items': [testgroup1.id, testgroup2.id]
                }
            }
        )
        self.assertEqual(4, group_models.FeedbackSet.objects.count())
        self.assertEqual(2, group_models.GroupComment.objects.count())
        group_comments = group_models.GroupComment.objects.all()
        last_feedbackset_group1 = AssignmentGroupCachedData.objects.get(group_id=testgroup1.id).last_feedbackset
        last_feedbackset_group2 = AssignmentGroupCachedData.objects.get(group_id=testgroup2.id).last_feedbackset
        self.assertEqual(last_feedbackset_group1.deadline_datetime, new_deadline)
        self.assertEqual(last_feedbackset_group2.deadline_datetime, new_deadline)
        self.assertEqual(last_feedbackset_group1.last_updated_by, testuser)
        self.assertEqual(last_feedbackset_group2.last_updated_by, testuser)
        self.assertEqual('You have been given a new attempt.', group_comments[0].text)
        self.assertEqual('You have been given a new attempt.', group_comments[1].text)

    def test_post_groups_published_raises_error(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        with self.assertRaises(http.Http404):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                cradmin_instance=self._get_mock_instance(testassignment),
                cradmin_app=self._get_mock_app(user=testuser),
                requestuser=testuser,
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                    'handle_deadline': self.handle_deadline
                },
                requestkwargs={
                    'data': {
                        'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                        'comment_text': 'You have been given a new attempt.',
                        'selected_items': [testgroup1.id, testgroup2.id]
                    }
                }
            )
        self.assertEqual(2, group_models.FeedbackSet.objects.count())


class TestManageDeadlineNewAttemptSingleGroup(ExaminerTestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineSingleGroupView
    handle_deadline = 'new-attempt'

    def test_info_box_not_showing_when_groups_should_be_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup1.id
            }
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-deadline-management-info-box'))

    def test_all_groups_added_to_form_hidden(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup1.id
            }
        )
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('value="{}"'.format(testgroup1.id), mockresponse.selector.one('#id_selected_items_0').__str__())

    def test_post(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup.id
            },
            requestkwargs={
                'data': {
                        'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                        'comment_text': 'You have been given a new attempt.',
                        'selected_items': [testgroup.id]
                    }
            }
        )
        self.assertEqual(2, group_models.FeedbackSet.objects.count())
        cached_data_group = core_models.AssignmentGroup.objects.get(id=testgroup.id).cached_data
        self.assertEqual(cached_data_group.first_feedbackset.deadline_datetime, testassignment.first_deadline)
        self.assertEqual(cached_data_group.last_feedbackset.deadline_datetime, new_deadline)
        self.assertEqual(cached_data_group.last_feedbackset.last_updated_by, testuser)

    def test_post_multiple_groups_raises_error(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        with self.assertRaises(http.Http404):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                cradmin_instance=self._get_mock_instance(testassignment),
                cradmin_app=self._get_mock_app(user=testuser),
                requestuser=testuser,
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                    'handle_deadline': self.handle_deadline,
                    'group_id': testgroup1.id
                },
                requestkwargs={
                    'data': {
                        'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                        'comment_text': 'You have been given a new attempt.',
                        'selected_items': [testgroup1.id, testgroup2.id]
                    }
                }
            )
        self.assertEqual(2, group_models.FeedbackSet.objects.count())
        cached_data_group1 = core_models.AssignmentGroup.objects.get(id=testgroup1.id).cached_data
        cached_data_group2 = core_models.AssignmentGroup.objects.get(id=testgroup2.id).cached_data
        self.assertNotEqual(cached_data_group1.last_feedbackset.deadline_datetime, new_deadline)
        self.assertNotEqual(cached_data_group2.last_feedbackset.deadline_datetime, new_deadline)

    def test_get_earliest_possible_deadline_last_deadline_in_past(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        last_feedbackset_last_deadline = testassignment.first_deadline
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(last_feedbackset_last_deadline),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup.id
            }
        )
        earliest_date = mockresponse.selector.list('.devilry-deadlinemanagement-suggested-deadline')[0] \
            .get('django-cradmin-setfieldvalue')
        converted_datetime = from_isoformat_noseconds(earliest_date)
        self.assertTrue(converted_datetime > timezone.now())
        self.assertTrue(converted_datetime < timezone.now() + timezone.timedelta(days=8))

    def test_get_all_suggested_deadlines_deadline_in_future(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        last_deadline = group_models.FeedbackSet.clean_deadline(timezone.now() + timedelta(days=1)).replace(second=0)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup,
                                                                          deadline_datetime=last_deadline)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testfeedbackset.deadline_datetime),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup.id
            }
        )
        added_days = 7
        for element in mockresponse.selector.list('.devilry-deadlinemanagement-suggested-deadline'):
            suggested_date = from_isoformat_noseconds(element.get('django-cradmin-setfieldvalue'))
            self.assertEqual(suggested_date, testfeedbackset.deadline_datetime + timedelta(days=added_days))
            added_days += 7

    def test_get_earliest_possible_deadline_last_deadline_in_future(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        last_feedbackset_last_deadline = group_models.FeedbackSet.clean_deadline(
            timezone.now() + timezone.timedelta(days=30)).replace(second=0)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(
            group=testgroup,
            deadline_datetime=last_feedbackset_last_deadline)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(last_feedbackset_last_deadline),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup.id
            }
        )
        earliest_date = mockresponse.selector.list('.devilry-deadlinemanagement-suggested-deadline')[0] \
            .get('django-cradmin-setfieldvalue')
        converted_datetime = from_isoformat_noseconds(earliest_date)
        self.assertEqual(testfeedbackset.deadline_datetime + timezone.timedelta(days=7), converted_datetime)

    def test_get_earliest_possible_deadline_uses_multiple_feedbacksets(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        now = timezone.now()
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        last_feedbackset_last_deadline = group_models.FeedbackSet.clean_deadline(now + timezone.timedelta(days=30))\
            .replace(second=0)
        testfeedbackset_last = group_mommy.feedbackset_new_attempt_published(
            group=testgroup,
            deadline_datetime=last_feedbackset_last_deadline)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(last_feedbackset_last_deadline),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup.id
            }
        )
        earliest_date = mockresponse.selector.list('.devilry-deadlinemanagement-suggested-deadline')[0] \
            .get('django-cradmin-setfieldvalue')
        converted_datetime = from_isoformat_noseconds(earliest_date)
        self.assertEqual(testfeedbackset_last.deadline_datetime + timezone.timedelta(days=7),
                          converted_datetime)


class TestManageDeadlineMoveDeadlineSingleGroup(ExaminerTestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineSingleGroupView
    handle_deadline = 'move-deadline'

    def test_info_box_not_showing_when_groups_should_be_excluded(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            requestuser=examiner_user,
            cradmin_app=self._get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup1.id
            }
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-deadline-management-info-box'))

    def test_all_groups_added_to_form_hidden(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup1.id
            }
        )
        self.assertIn('type="hidden"', mockresponse.selector.one('#id_selected_items_0').__str__())
        self.assertIn('value="{}"'.format(testgroup1.id), mockresponse.selector.one('#id_selected_items_0').__str__())

    def test_post(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup.id
            },
            requestkwargs={
                'data': {
                    'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                    'comment_text': 'You have been given a new attempt.',
                    'selected_items': [testgroup.id]
                }
            }
        )
        self.assertEqual(1, group_models.FeedbackSet.objects.count())
        cached_data_group = core_models.AssignmentGroup.objects.get(id=testgroup.id).cached_data
        self.assertEqual(cached_data_group.last_feedbackset, cached_data_group.first_feedbackset)
        self.assertEqual(cached_data_group.last_feedbackset.deadline_datetime, new_deadline)
        self.assertEqual(cached_data_group.last_feedbackset.last_updated_by, testuser)

    def test_post_multiple_groups_raises_error(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        new_deadline = timezone.now() + timezone.timedelta(days=3)
        new_deadline = new_deadline.replace(microsecond=0)
        with self.assertRaises(http.Http404):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                cradmin_instance=self._get_mock_instance(testassignment),
                cradmin_app=self._get_mock_app(user=testuser),
                requestuser=testuser,
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_url_string(testassignment.first_deadline),
                    'handle_deadline': self.handle_deadline,
                    'group_id': testgroup1.id
                },
                requestkwargs={
                    'data': {
                        'new_deadline': isoformat_withseconds(timezone.localtime(new_deadline)),
                        'comment_text': 'You have been given a new attempt.',
                        'selected_items': [testgroup1.id, testgroup2.id]
                    }
                }
            )
        self.assertEqual(2, group_models.FeedbackSet.objects.count())
        cached_data_group1 = core_models.AssignmentGroup.objects.get(id=testgroup1.id).cached_data
        cached_data_group2 = core_models.AssignmentGroup.objects.get(id=testgroup2.id).cached_data
        self.assertNotEqual(cached_data_group1.last_feedbackset.deadline_datetime, new_deadline)
        self.assertNotEqual(cached_data_group2.last_feedbackset.deadline_datetime, new_deadline)

    def test_get_earliest_suggested_deadline_count(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # The final deadline for the first feedbackset
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testfeedbackset.deadline_datetime),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup.id
            }
        )
        self.assertEqual(mockresponse.selector.count('.devilry-deadlinemanagement-suggested-deadline'), 4)

    def test_get_earliest_suggested_deadline_last_deadline_in_past(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testfeedbackset.deadline_datetime),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup.id
            }
        )
        earliest_date = mockresponse.selector.list('.devilry-deadlinemanagement-suggested-deadline')[0]\
            .get('django-cradmin-setfieldvalue')
        converted_datetime = from_isoformat_noseconds(earliest_date)
        now_with_same_time_as_deadline = datetimeutils.datetime_with_same_time(
            testfeedbackset.deadline_datetime, timezone.now())
        self.assertEqual(now_with_same_time_as_deadline + timedelta(days=7), converted_datetime)

    def test_get_all_suggested_deadlines_deadline_in_future(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        last_deadline = group_models.FeedbackSet.clean_deadline(timezone.now() + timedelta(days=1)).replace(second=0)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup,
                                                                            deadline_datetime=last_deadline)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(testfeedbackset.deadline_datetime),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup.id
            }
        )
        added_days = 7
        for element in mockresponse.selector.list('.devilry-deadlinemanagement-suggested-deadline'):
            suggested_date = from_isoformat_noseconds(element.get('django-cradmin-setfieldvalue'))
            self.assertEqual(suggested_date, testfeedbackset.deadline_datetime + timedelta(days=added_days))
            added_days += 7

    def test_get_earliest_possible_deadline_last_deadline_in_future(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # The final deadline for the first feedbackset
        first_feedbackset_last_deadline = group_models.FeedbackSet.clean_deadline(
            timezone.now() + timezone.timedelta(days=10)).replace(second=0)
        testfeedbackset1 = group_mommy.feedbackset_first_attempt_published(
            group=testgroup,
            deadline_datetime=first_feedbackset_last_deadline)

        # The current final deadline for the last feedbackset
        last_feedbackset_last_deadline = group_models.FeedbackSet.clean_deadline(
            timezone.now() + timezone.timedelta(days=30)).replace(second=0)
        testfeedbackset2 = group_mommy.feedbackset_new_attempt_published(
            group=testgroup,
            deadline_datetime=last_feedbackset_last_deadline)

        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self._get_mock_instance(testassignment),
            cradmin_app=self._get_mock_app(user=testuser),
            requestuser=testuser,
            viewkwargs={
                'deadline': datetimeutils.datetime_to_url_string(last_feedbackset_last_deadline),
                'handle_deadline': self.handle_deadline,
                'group_id': testgroup.id
            }
        )
        earliest_date = mockresponse.selector.list('.devilry-deadlinemanagement-suggested-deadline')[0]\
            .get('django-cradmin-setfieldvalue')
        converted_datetime = from_isoformat_noseconds(earliest_date)
        self.assertEqual(testfeedbackset2.deadline_datetime + timedelta(days=7), converted_datetime)
