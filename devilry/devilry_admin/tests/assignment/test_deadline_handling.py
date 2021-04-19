import unittest

import mock
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_admin.views.assignment import deadline_handling


@unittest.skip('Add when issue 978 is resolved')
class TestAssignmentDeadlineHandlingUpdateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = deadline_handling.AssignmentDeadlineHandlingUpdateView

    def test_title(self):
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser,
            viewkwargs={'pk': testassignment.id})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                          'Edit deadline handling')

    def test_user_is_periodadmin_raises_404(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        baker.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=baker.make('devilry_account.PeriodPermissionGroup',
                                              period=testassignment.parentnode).permissiongroup)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=testuser,
                viewkwargs={'pk': testassignment.id})

    def test_user_is_subjectadmin_does_not_raise_404(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        baker.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=baker.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                              subject=testassignment.parentnode.parentnode).permissiongroup)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser,
            viewkwargs={'pk': testassignment.id})

    def test_user_is_departmentadmin_does_not_raise_404(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        baker.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=baker.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
                                              subject=testassignment.parentnode.parentnode).permissiongroup)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser,
            viewkwargs={'pk': testassignment.id})

    def test_user_is_superuser_does_not_raise_404(self):
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser,
            viewkwargs={'pk': testassignment.id})

    def test_post_deadline_handling_soft_to_hard(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        baker.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=baker.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                              subject=testassignment.parentnode.parentnode).permissiongroup)
        messagesmock = mock.MagicMock()
        self.assertEqual(testassignment.deadline_handling, Assignment.DEADLINEHANDLING_SOFT)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            requestuser=testuser,
            viewkwargs={'pk': testassignment.id},
            requestkwargs={
                'data': {
                    'deadline_handling': 1
                }
            },
            messagesmock=messagesmock
        )
        testassignment.refresh_from_db()
        self.assertEqual(testassignment.deadline_handling, Assignment.DEADLINEHANDLING_HARD)
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Changed deadline handling from "SOFT" to "HARD".',
            ''
        )

    def test_post_deadline_handling_hard_to_soft(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           deadline_handling=Assignment.DEADLINEHANDLING_HARD)
        baker.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=baker.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                              subject=testassignment.parentnode.parentnode).permissiongroup)
        messagesmock = mock.MagicMock()
        self.assertEqual(testassignment.deadline_handling, Assignment.DEADLINEHANDLING_HARD)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            requestuser=testuser,
            viewkwargs={'pk': testassignment.id},
            requestkwargs={
                'data': {
                    'deadline_handling': 0
                }
            },
            messagesmock=messagesmock
        )
        testassignment.refresh_from_db()
        self.assertEqual(testassignment.deadline_handling, Assignment.DEADLINEHANDLING_SOFT)
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Changed deadline handling from "HARD" to "SOFT".',
            ''
        )
