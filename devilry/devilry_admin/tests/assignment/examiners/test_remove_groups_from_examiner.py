import mock
from django import test
from django.contrib import messages
from django.http import Http404
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core.models import Examiner
from devilry.devilry_admin.views.assignment.examiners import remove_groups_from_examiner


class TestRemoveGroupsToExaminerView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    NOTE: Much of the functionality for this view is tested in
    test_groupview_base.test_groupviewmixin.TestGroupViewMixin
    and test_basemultiselectview.TestBaseMultiselectView.
    """
    viewclass = remove_groups_from_examiner.RemoveGroupsToExaminerView

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_404_if_relatedexaminer_is_inactive(self):
        testassignment = baker.make('core.Assignment', long_name='Test Assignment')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period,
                                     active=False)
        baker.make('core.AssignmentGroup', parentnode=testassignment)
        with self.assertRaises(Http404):
            self.mock_getrequest(
                cradmin_role=testassignment,
                viewkwargs={'relatedexaminer_id': relatedexaminer.id},
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_title(self):
        testassignment = baker.make('core.Assignment', long_name='Test Assignment')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period,
                                     user__fullname='Test User')
        baker.make('core.Examiner', assignmentgroup__parentnode=testassignment, relatedexaminer=relatedexaminer)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertIn(
            'Remove students from Test User',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = baker.make('core.Assignment', long_name='Test Assignment')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period,
                                     user__fullname='Test User')
        baker.make('core.Examiner', assignmentgroup__parentnode=testassignment, relatedexaminer=relatedexaminer)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Remove students from Test User',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_submit_button_text(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period)
        baker.make('core.Examiner', assignmentgroup__parentnode=testassignment, relatedexaminer=relatedexaminer)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Remove students',
            mockresponse.selector.one('.cradmin-legacy-multiselect2-target-formfields .btn').alltext_normalized)

    def test_exclude_groups_that_does_not_have_the_examiner(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period)
        baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_with_the_examiner = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Examiner', assignmentgroup=group_with_the_examiner, relatedexaminer=relatedexaminer)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_no_groups_on_examiner(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period)
        baker.make('core.AssignmentGroup', parentnode=testassignment)
        messagesmock = mock.MagicMock()
        self.mock_http302_getrequest(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        messagesmock.add.assert_called_once_with(
            messages.INFO,
            'No students to remove.',
            '')

    def test_get_querycount(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period)
        baker.make('core.AssignmentGroup', parentnode=testassignment, _quantity=10)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=relatedexaminer)
        with self.assertNumQueries(11):
            self.mock_getrequest(
                cradmin_role=testassignment,
                viewkwargs={'relatedexaminer_id': relatedexaminer.id},
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_post_ok(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer=relatedexaminer)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer=relatedexaminer)
        self.assertEqual(2, Examiner.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            requestkwargs={
                'data': {'selected_items': [str(testgroup1.id), str(testgroup2.id)]}
            })
        self.assertEqual(0, Examiner.objects.count())

    def test_post_successmessage_no_projectgroups(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup1)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer=relatedexaminer)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer=relatedexaminer)
        baker.make('core.Candidate', assignment_group=testgroup2)

        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            requestkwargs={
                'data': {'selected_items': [str(testgroup1.id), str(testgroup2.id)]}
            })
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Removed 2 students.',
            '')

    def test_post_successmessage_with_single_projectgroups(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup)
        baker.make('core.Candidate', assignment_group=testgroup)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=relatedexaminer)

        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            requestkwargs={
                'data': {'selected_items': [str(testgroup.id)]}
            })
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Removed 1 project group with 2 students.',
            '')

    def test_post_successmessage_with_multiple_projectgroups(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup1, _quantity=10)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer=relatedexaminer)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup2, _quantity=8)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer=relatedexaminer)

        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            requestkwargs={
                'data': {'selected_items': [str(testgroup1.id), str(testgroup2.id)]}
            })
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Removed 2 project groups with 18 students.',
            '')

    def test_post_querycount(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer = baker.make('core.RelatedExaminer', period=testassignment.period)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup1, _quantity=10)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer=relatedexaminer)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup2, _quantity=10)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer=relatedexaminer)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup3, _quantity=3)
        baker.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer=relatedexaminer)
        testgroup4 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup4, _quantity=3)
        baker.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer=relatedexaminer)

        with self.assertNumQueries(6):
            self.mock_postrequest(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                viewkwargs={'relatedexaminer_id': relatedexaminer.id},
                requestkwargs={
                    'data': {'selected_items': [str(testgroup1.id), str(testgroup2.id),
                                                str(testgroup3.id), str(testgroup4.id)]}
                })
