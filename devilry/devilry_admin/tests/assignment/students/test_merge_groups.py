import mock
from django import test
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_admin.views.assignment.students import merge_groups
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestMergeGroupsView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    NOTE: Much of the functionality for this view is tested in
    test_groupview_base.test_groupviewmixin.TestGroupViewMixin
    and test_basemultiselectview.TestBaseMultiselectView.
    """
    viewclass = merge_groups.MergeGroupsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertIn(
            'Organize students in project groups',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Organize students in project groups',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_groups_sanity(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.AssignmentGroup', parentnode=testassignment, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            3,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_submit_button_text(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'Create project group',
            mockresponse.selector.one('.django-cradmin-multiselect2-target-formfields .btn').alltext_normalized)

    def test_error_merge_less_than_2_groups(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment, id=10)
        core_mommy.candidate(group=group)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            messagesmock=messagesmock,
            requestkwargs={
                'data': {
                    'selected_items': [10]
                }
            })
        messagesmock.add.assert_called_once_with(
            messages.WARNING,
            'Cannot merge less than 2 groups',
            ''
        )

    def test_success_merge_2_groups_message(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment, id=10)
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment, id=11)
        core_mommy.candidate(group=group1, shortname='April@example.com', fullname='April')
        core_mommy.candidate(group=group2, shortname='Dewey@example.com', fullname='Dewey')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            messagesmock=messagesmock,
            requestkwargs={
                'data': {
                    'selected_items': [10, 11]
                }
            })
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'A group with April@example.com, Dewey@example.com has been created!',
            ''
        )

    def test_success_merge_2_groups_db(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment, id=10)
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment, id=11)
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group2)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            requestkwargs={
                'data': {
                    'selected_items': [10, 11]
                }
            })
        self.assertTrue(AssignmentGroup.objects.filter(id=group1.id).exists())
        self.assertFalse(AssignmentGroup.objects.filter(id=group2.id).exists())
        self.assertEquals(AssignmentGroup.objects.get(id=group1.id).candidates.count(), 2)
        self.assertEquals(AssignmentGroup.objects.get(id=group1.id).feedbackset_set.count(), 3)

    def test_success_merge_multiple_groups_db(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group4 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group2)
        core_mommy.candidate(group=group3)
        core_mommy.candidate(group=group4)
        core_mommy.examiner(group=group1)
        core_mommy.examiner(group=group2)
        core_mommy.examiner(group=group3)
        core_mommy.examiner(group=group4)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            requestkwargs={
                'data': {
                    'selected_items': [group1.id, group2.id, group3.id, group4.id]
                }
            })
        self.assertFalse(AssignmentGroup.objects.filter(id=group2.id).exists())
        self.assertFalse(AssignmentGroup.objects.filter(id=group3.id).exists())
        self.assertFalse(AssignmentGroup.objects.filter(id=group4.id).exists())
        self.assertTrue(AssignmentGroup.objects.filter(id=group1.id).exists())

    def test_candidate_count_filter(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group2)
        core_mommy.examiner(group=group2)
        core_mommy.examiner(group=group2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            viewkwargs={
                'filters_string': 'candidatecount-eq-2'
            })
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_examiner_count_filter(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group2)
        core_mommy.examiner(group=group2)
        core_mommy.examiner(group=group2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            viewkwargs={
                'filters_string': 'examinercount-eq-2'
            })
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_candidate_count_filter_after_merge(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group2)
        core_mommy.examiner(group=group2)
        core_mommy.examiner(group=group1)
        AssignmentGroup.merge_groups([group1, group2])
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            viewkwargs={
                'filters_string': 'examinercount-eq-2'
            })
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_examiner_count_filter_after_merge(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group2)
        core_mommy.examiner(group=group2)
        core_mommy.examiner(group=group1)
        AssignmentGroup.merge_groups([group1, group2])
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            viewkwargs={
                'filters_string': 'candidatecount-eq-3'
            })
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))


class TestMergeGroupsAnonymization(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = merge_groups.MergeGroupsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_404_anonymizationmode_fully_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_404_anonymizationmode_semi_periodadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))

    def test_404_anonymizationmode_fully_periodadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))

    def test_anonymizationmode_fully_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_semi_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_off_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_semi_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_anonymizationmode_off_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_anonymizationmode_off_period(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))
