import mock
from django.contrib import messages
from django.http import Http404
from django.test import TestCase
from django.conf import settings
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core.models import AssignmentGroup, Candidate, Assignment
from devilry.devilry_admin.views.assignment.students import split_group
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


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
        selectlist = [elem.alltext_normalized for elem in mockresponse.selector.list('#id_students > option')]
        self.assertIn(candidate1.relatedstudent.user.get_displayname(), selectlist)
        self.assertIn(candidate2.relatedstudent.user.get_displayname(), selectlist)
        self.assertIn(candidate3.relatedstudent.user.get_displayname(), selectlist)

    def test_cannot_pop_candidate_if_there_is_only_one(self):
        testgroup = mommy.make('core.AssignmentGroup')
        candidate = core_mommy.candidate(group=testgroup)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testgroup.parentnode,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            messagesmock=messagesmock,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data':
                    {'students': candidate.id}
            }
        )
        messagesmock.add.assert_called_once_with(
            messages.WARNING,
            'Cannot split student if there is less than 2 students in project group.',
            ''
        )

    def test_pop_candidate_sanity(self):
        testgroup = mommy.make('core.AssignmentGroup')
        core_mommy.candidate(group=testgroup)
        candidate = core_mommy.candidate(group=testgroup, shortname='sirtoby', fullname='sir. Toby')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testgroup.parentnode,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            messagesmock=messagesmock,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data':
                    {'students': candidate.id}
            }
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            '{} was removed from the project group'.format(candidate.relatedstudent.user.get_displayname()),
            ''
        )

    def test_pop_candidate_db(self):
        testgroup = mommy.make('core.AssignmentGroup')
        core_mommy.candidate(group=testgroup)
        candidate = core_mommy.candidate(group=testgroup, shortname='sirtoby', fullname='sir. Toby')
        self.mock_http302_postrequest(
            cradmin_role=testgroup.parentnode,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data':
                    {'students': candidate.id}
            }
        )
        candidate = Candidate.objects.get(id=candidate.id)
        self.assertNotEqual(candidate.assignment_group, testgroup)
        testgroup = AssignmentGroup.objects.get(id=testgroup.id)
        self.assertEqual(1, testgroup.cached_data.candidate_count);


class TestSplitGroupAnonymization(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = split_group.SplitGroupView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_404_anonymizationmode_fully_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                viewkwargs={'pk': testgroup.id},
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_404_anonymizationmode_semi_periodadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                viewkwargs={'pk': testgroup.id},
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))

    def test_404_anonymizationmode_fully_periodadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                viewkwargs={'pk': testgroup.id},
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))

    def test_anonymizationmode_fully_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'pk': testgroup.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_semi_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'pk': testgroup.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_off_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'pk': testgroup.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_semi_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'pk': testgroup.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_anonymizationmode_off_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'pk': testgroup.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_anonymizationmode_off_period(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'pk': testgroup.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))
