from django.test import TestCase
from django_cradmin import cradmin_testhelpers

from devilry.devilry_admin.views.assignment import overview
from devilry.project.develop.testhelpers.corebuilder import AssignmentBuilder, UserBuilder, PeriodBuilder


class TestOverviewApp(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_title(self):
        assignmentbuilder = AssignmentBuilder.quickadd_ducku_duck1010_active_assignment1()
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignmentbuilder.assignment)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized, 'duck1010.active.assignment1')

    def test_h1(self):
        assignmentbuilder = AssignmentBuilder.quickadd_ducku_duck1010_active_assignment1()
        assignmentbuilder.update(long_name="DUCK 1010")
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignmentbuilder.assignment)
        self.assertEquals(mockresponse.selector.one('h1').alltext_normalized, 'DUCK 1010')

    def test_assignment_meta_has_two_students(self):
        assignmentbuilder = AssignmentBuilder.quickadd_ducku_duck1010_active_assignment1()
        UserBuilder('examiner1').user
        assignmentbuilder.add_group()
        assignmentbuilder.add_group()
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignmentbuilder.assignment)
        self.assertTrue(mockresponse.selector.one('#devilry_admin_assignment_meta p').alltext_normalized.startswith('2 students'))

    def test_assignment_meta_one_examiner_configured(self):
        examiner1 = UserBuilder('examiner1').user
        week1builder = PeriodBuilder.quickadd_ducku_duck1010_active().add_assignment('week1')
        group1 = week1builder.add_group()
        week1builder.add_group()
        group1.add_examiners(examiner1)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=week1builder.assignment)
        self.assertTrue(mockresponse.selector.one('.devilry-admin-assignment-examiners-exists').alltext_normalized.startswith('1 examiner'))

