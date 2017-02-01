import htmls
import mock
from django import forms
from django.contrib import messages
from django.http import Http404
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import AssignmentGroup, Candidate, Assignment
from devilry.devilry_admin.views.assignment.students import split_group
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.apps.core import devilry_core_mommy_factories as core_mommy


class TestSplitGroup(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = split_group.SplitGroupView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'pk': testgroup.id}
        )
        self.assertIn(
            'Split students from project group',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'pk': testgroup.id}
        )
        self.assertIn(
            'Split students from project group',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_submit_button_text(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'pk': testgroup.id}
        )
        self.assertIn(
            'Split',
            mockresponse.selector.one('#submit-id-split').alltext_normalized)

    def test_select_candidate(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate1 = core_mommy.candidate(group=testgroup, shortname='mrcool', fullname='Mr. Cool')
        candidate2 = core_mommy.candidate(group=testgroup, shortname='mrman', fullname='Mr. Man')
        candidate3 = core_mommy.candidate(group=testgroup, shortname='sirtoby', fullname='sir. Toby')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'pk': testgroup.id}
        )
        selectlist = [elem.alltext_normalized for elem in mockresponse.selector.list('#id_candidates > option')]
        self.assertIn(candidate1.relatedstudent.user.get_displayname(), selectlist)
        self.assertIn(candidate2.relatedstudent.user.get_displayname(), selectlist)
        self.assertIn(candidate3.relatedstudent.user.get_displayname(), selectlist)

    def test_fully_anonymous(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        with self.assertRaises(Http404):
            self.mock_getrequest(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                viewkwargs={'pk': testgroup.id}
            )

