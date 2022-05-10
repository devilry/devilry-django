import unittest

import mock
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment import examiner_selfassign


class TestAssignmentExaminerSelfAssignUpdateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = examiner_selfassign.AssignmentExaminerSelfAssignUpdateView

    def test_title(self):
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser,
            viewkwargs={'pk': testassignment.id})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                          'Edit examiner self-assign')

    def test_post_enable_examiner_self_assign(self):
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            viewkwargs={'pk': testassignment.id},
            requestuser=testuser,
            requestkwargs={
                'data': {
                    'examiners_can_self_assign': True,
                    'examiner_self_assign_limit': 1
                }
            },
            messagesmock=messagesmock
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Examiner self-assign enabled with self-assign limit set to 1.',
            ''
        )
        testassignment.refresh_from_db()
        self.assertTrue(testassignment.examiners_can_self_assign)
    
    def test_post_enable_examiner_self_assign_with_nondefault_limit(self):
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            viewkwargs={'pk': testassignment.id},
            requestuser=testuser,
            requestkwargs={
                'data': {
                    'examiners_can_self_assign': True,
                    'examiner_self_assign_limit': 12
                }
            },
            messagesmock=messagesmock
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Examiner self-assign enabled with self-assign limit set to 12.',
            ''
        )
        testassignment.refresh_from_db()
        self.assertTrue(testassignment.examiners_can_self_assign)
    
    def test_post_update_limit_only(self):
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            examiners_can_self_assign=True,
            examiner_self_assign_limit=3
        )
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            viewkwargs={'pk': testassignment.id},
            requestuser=testuser,
            requestkwargs={
                'data': {
                    'examiners_can_self_assign': True,
                    'examiner_self_assign_limit': 12
                }
            },
            messagesmock=messagesmock
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Examiner self-assign limit changed from 3 to 12.',
            ''
        )
        testassignment.refresh_from_db()
        self.assertTrue(testassignment.examiners_can_self_assign)
        self.assertEqual(testassignment.examiner_self_assign_limit, 12)
    
    def test_post_disable_selfassign(self):
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            examiners_can_self_assign=True,
            examiner_self_assign_limit=3
        )
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            viewkwargs={'pk': testassignment.id},
            requestuser=testuser,
            requestkwargs={
                'data': {
                    'examiners_can_self_assign': False,
                    'examiner_self_assign_limit': 12
                }
            },
            messagesmock=messagesmock
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Examiner self-assign disabled.',
            ''
        )
        testassignment.refresh_from_db()
        self.assertFalse(testassignment.examiners_can_self_assign)
