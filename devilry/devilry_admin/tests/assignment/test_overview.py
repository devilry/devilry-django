from django.test import TestCase
from django_cradmin import cradmin_testhelpers

from devilry.devilry_admin.views.assignment import overview
from devilry.project.develop.testhelpers.corebuilder import AssignmentBuilder


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
