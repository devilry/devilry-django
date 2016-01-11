from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy
from devilry.apps.core.mommy_recipes import assignment_activeperiod_end
from devilry.apps.core import models as coremodels
from devilry.devilry_admin.views.assignment import overview
from devilry.project.develop.testhelpers.corebuilder import AssignmentBuilder, UserBuilder, PeriodBuilder


class TestOverviewApp(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_title(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end',
                                       short_name="testassignment",
                                       parentnode__short_name="testperiod",  # Period
                                       parentnode__parentnode__short_name="testsubject"  # Subject
                                       )
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          'testsubject.testperiod.testassignment')

    def test_h1(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end',
                                       long_name="TESTASSIGNMENT",
                                       )
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEquals(mockresponse.selector.one('h1').alltext_normalized, 'TESTASSIGNMENT')

    def test_assignment_meta_has_two_students(self):
        assignment = mommy.make('core.Assignment')
        mommy.make('core.AssignmentGroup', parentnode=assignment, _quantity=2)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertTrue(
                mockresponse.selector.one('#devilry_admin_assignment_meta p').alltext_normalized.startswith(
                    '2 students'))

    def test_assignment_meta_has_no_students(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertTrue(
                mockresponse.selector.one('#devilry_admin_assignment_meta p').alltext_normalized.startswith(
                    '0 students'))

    def test_assignment_meta_one_examiner_configured(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        examiner1 = mommy.make('core.Examiner')
        assignment_group = mommy.make('core.AssignmentGroup', parentnode=assignment, examiners=examiner1)
        assignment_group.examiners.add(examiner1)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertTrue(
                mockresponse.selector.one('.devilry-admin-assignment-examiners-exists').alltext_normalized.startswith(
                        '1 examiner'))

    def test_assignment_meta_no_examiner_configured(self):
        assignment = mommy.make('core.Assignment') #mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertFalse(
                mockresponse.selector.exists('.devilry-admin-assignment-examiners-exists'))
