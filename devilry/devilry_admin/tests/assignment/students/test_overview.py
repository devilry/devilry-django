from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_admin.views.assignment.students import overview


class TestOverview(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_title(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertIn(
            'Students on Test Assignment',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Students on Test Assignment',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_grouplist_no_groups(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'No students',
            mockresponse.selector.one('.django-cradmin-listbuilderview-no-items-message').alltext_normalized)
        self.assertFalse(
            mockresponse.selector.exists('.django-cradmin-listbuilder-list'))

    def test_grouplist_has_groups_sanity(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertFalse(
            mockresponse.selector.exists('.django-cradmin-listbuilderview-no-items-message'))
        self.assertTrue(
            mockresponse.selector.exists('.django-cradmin-listbuilder-list'))

    # def test_grouplist_render_single

    # def test_grouplist_ordering

    # def test_grouplist_pagination(self):
