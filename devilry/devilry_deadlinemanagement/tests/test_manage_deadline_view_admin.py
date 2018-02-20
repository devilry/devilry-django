# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django import test
from django import http
from django.conf import settings
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_account import models as account_models
from devilry.apps.core import models as core_models
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_dbcache.models import AssignmentGroupCachedData
from devilry.devilry_deadlinemanagement.views import manage_deadline_view
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.utils import datetimeutils
from devilry.utils.datetimeutils import isoformat_withseconds


class AdminTestCaseMixin(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineAllGroupsView
    handle_deadline = 'new-attempt'

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def _get_mock_instance(self, assignment):
        mock_instance = mock.MagicMock()
        mock_instance.get_devilryrole_type.return_value = 'admin'
        mock_instance.assignment = assignment
        return mock_instance

    def _get_mock_app(self, user=None):
        mock_app = mock.MagicMock()
        mock_app.get_devilryrole.return_value = 'admin'
        mock_app.get_accessible_group_queryset.return_value = core_models.AssignmentGroup.objects\
            .filter_user_is_admin(user=user)
        return mock_app

    def _create_department_admin(self, period):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        subject = period.parentnode
        permissiongroup = mommy.make(
            'devilry_account.SubjectPermissionGroup',
            permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
            subject=subject).permissiongroup
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=permissiongroup)
        return testuser

    def _create_subject_admin(self, period):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        subject = period.parentnode
        permissiongroup = mommy.make(
            'devilry_account.SubjectPermissionGroup',
            permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN,
            subject=subject
        ).permissiongroup
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=permissiongroup)
        return testuser

    def _create_period_admin(self, period):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        permissiongroup = mommy.make(
            'devilry_account.PeriodPermissionGroup',
            permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN,
            period=period
        ).permissiongroup
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=permissiongroup)
        return testuser

    def _get_admin_user(self, period):
        return self._create_period_admin(period)


class TestManageDeadlineNewAttemptAllGroupsView(AdminTestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineAllGroupsView
    handle_deadline = 'new-attempt'

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
        testuser = self._get_admin_user(testassignment.parentnode)
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
        testuser = self._get_admin_user(testassignment.parentnode)
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
        testuser = self._get_admin_user(testassignment.parentnode)
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
        self.assertEquals(3, feedbacksets.count())
        group1 = core_models.AssignmentGroup.objects.get(id=testgroup1.id)
        group2 = core_models.AssignmentGroup.objects.get(id=testgroup2.id)
        self.assertEquals(new_deadline, group1.cached_data.last_feedbackset.deadline_datetime)
        self.assertNotEquals(new_deadline, group2.cached_data.last_feedbackset.deadline_datetime)

    def test_post_groups_unpublished_raises_error(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = self._get_admin_user(testassignment.parentnode)
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
        self.assertEquals(2, group_models.FeedbackSet.objects.count())


class TestSubjectAdminNewAttemptAllGroupsView(TestManageDeadlineNewAttemptAllGroupsView):
    def _get_admin_user(self, period):
        return self._create_subject_admin(period)


class TestDepartmentAdminNewAttemptAllGroupsView(TestManageDeadlineNewAttemptAllGroupsView):
    def _get_admin_user(self, period):
        return self._create_department_admin(period)


class TestManageDeadlineMoveDeadlineAllGroupsView(AdminTestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineAllGroupsView
    handle_deadline = 'move-deadline'

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
        testuser = self._get_admin_user(testassignment.parentnode)
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
        testuser = self._get_admin_user(testassignment.parentnode)
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
        testuser = self._get_admin_user(testassignment.parentnode)
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
        self.assertEquals(2, feedbacksets.count())
        group1 = core_models.AssignmentGroup.objects.get(id=testgroup1.id)
        group2 = core_models.AssignmentGroup.objects.get(id=testgroup2.id)
        self.assertEquals(group1.cached_data.last_feedbackset, group1.cached_data.first_feedbackset)
        self.assertEquals(new_deadline, group1.cached_data.last_feedbackset.deadline_datetime)
        self.assertNotEquals(new_deadline, group2.cached_data.last_feedbackset.deadline_datetime)

    def test_post_groups_published_raises_error(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = self._get_admin_user(testassignment.parentnode)
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
        self.assertEquals(2, group_models.FeedbackSet.objects.count())


class TestSubjectAdminMoveDeadlinAllGroupsView(TestManageDeadlineMoveDeadlineAllGroupsView):
    def _get_admin_user(self, period):
        return self._create_subject_admin(period)


class TestDepartmentAdminMoveDeadlineAllGroupsView(TestManageDeadlineMoveDeadlineAllGroupsView):
    def _get_admin_user(self, period):
        return self._create_department_admin(period)


class TestManageDeadlineNewAttemptFromPreviousView(AdminTestCaseMixin):
    """
    Tests posting data from another view, and the actual posting in this view.
    """
    viewclass = manage_deadline_view.ManageDeadlineFromPreviousView
    handle_deadline = 'new-attempt'

    def test_post_from_previous_view_selected_groups_are_hidden(self):
        # By adding the post_type_received_data to the key, we are simulating that the
        # post comes from a different view.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup2)
        testuser = self._get_admin_user(testassignment.parentnode)
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
        testuser = self._get_admin_user(testassignment.parentnode)
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
        self.assertEquals(4, group_models.FeedbackSet.objects.count())
        self.assertEquals(2, group_models.GroupComment.objects.count())
        group_comments = group_models.GroupComment.objects.all()
        last_feedbackset_group1 = AssignmentGroupCachedData.objects.get(group_id=testgroup1.id).last_feedbackset
        last_feedbackset_group2 = AssignmentGroupCachedData.objects.get(group_id=testgroup2.id).last_feedbackset
        self.assertEquals(last_feedbackset_group1.deadline_datetime, new_deadline)
        self.assertEquals(last_feedbackset_group2.deadline_datetime, new_deadline)
        self.assertEqual(last_feedbackset_group1.last_updated_by, testuser)
        self.assertEqual(last_feedbackset_group2.last_updated_by, testuser)
        self.assertEquals('You have been given a new attempt.', group_comments[0].text)
        self.assertEquals('You have been given a new attempt.', group_comments[1].text)

    def test_post_groups_published_raises_error(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = self._get_admin_user(testassignment.parentnode)
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
        self.assertEquals(2, group_models.FeedbackSet.objects.count())


class TestSubjectAdminNewAttemptFromPreviousView(TestManageDeadlineNewAttemptFromPreviousView):
    def _get_admin_user(self, period):
        return self._create_subject_admin(period)


class TestDepartmentAdminNewAttemptFromPreviousView(TestManageDeadlineNewAttemptFromPreviousView):
    def _get_admin_user(self, period):
        return self._create_department_admin(period)


class TestManageDeadlineMoveDeadlineFromPreviousView(AdminTestCaseMixin):
    viewclass = manage_deadline_view.ManageDeadlineFromPreviousView
    handle_deadline = 'move-deadline'

    def test_post_from_previous_view_selected_groups_are_hidden(self):
        # By adding the post_type_received_data to the key, we are simulating that the
        # post comes from a different view.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = self._get_admin_user(testassignment.parentnode)
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
        testuser = self._get_admin_user(testassignment.parentnode)
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
        self.assertEquals(4, group_models.FeedbackSet.objects.count())
        self.assertEquals(2, group_models.GroupComment.objects.count())
        group_comments = group_models.GroupComment.objects.all()
        last_feedbackset_group1 = AssignmentGroupCachedData.objects.get(group_id=testgroup1.id).last_feedbackset
        last_feedbackset_group2 = AssignmentGroupCachedData.objects.get(group_id=testgroup2.id).last_feedbackset
        self.assertEquals(last_feedbackset_group1.deadline_datetime, new_deadline)
        self.assertEquals(last_feedbackset_group2.deadline_datetime, new_deadline)
        self.assertEqual(last_feedbackset_group1.last_updated_by, testuser)
        self.assertEqual(last_feedbackset_group2.last_updated_by, testuser)
        self.assertEquals('You have been given a new attempt.', group_comments[0].text)
        self.assertEquals('You have been given a new attempt.', group_comments[1].text)

    def test_post_groups_published_raises_error(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup1)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup2)
        testuser = self._get_admin_user(testassignment.parentnode)
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
        self.assertEquals(2, group_models.FeedbackSet.objects.count())


class TestSubjectAdminMoveDeadlineFromPreviousView(TestManageDeadlineMoveDeadlineFromPreviousView):
    def _get_admin_user(self, period):
        return self._create_subject_admin(period)


class TestDepartmentAdminMoveDeadlineFromPreviousView(TestManageDeadlineMoveDeadlineFromPreviousView):
    def _get_admin_user(self, period):
        return self._create_department_admin(period)
