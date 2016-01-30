import mock
from django import test
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_admin.views.assignment.examiners import examinerdetails


class TestExaminerDetailsView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    NOTE: Most of the functionality for this view is tested in
    devilry.devilry_admin.tests.assignment.students.test_groupview_base.test_groupviewmixin.TestGroupViewMixin
    and
    devilry.devilry_admin.tests.assignment.students.test_groupview_base.test_baseinforview.TestBaseInfoView
    """
    viewclass = examinerdetails.ExaminerDetailsView

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testassignment = mommy.make('core.Assignment')
        relatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.period,
                                     user__fullname='Test User')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertIn(
            'Test User - examiner',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        relatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.period,
                                     user__fullname='Test User')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Test User (examiner)',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_buttonbar_add_students_link(self):
        testassignment = mommy.make('core.Assignment')
        relatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.period,
                                     user__fullname='Test User')
        mock_cradmin_instance = self.__mockinstance_with_devilryrole('departmentadmin')

        def mock_reverse_url(appname, viewname, args, kwargs):
            return '/{}/{}/{}'.format(appname, kwargs.get('relatedexaminer_id'), viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            '/add_groups_to_examiner/{}/INDEX'.format(relatedexaminer.id),
            mockresponse.selector
            .one('#devilry_admin_assignment_examinerdetails_button_add_students')['href'])

    def test_buttonbar_add_students_text(self):
        testassignment = mommy.make('core.Assignment')
        relatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Add students',
            mockresponse.selector
            .one('#devilry_admin_assignment_examinerdetails_button_add_students').alltext_normalized)

    def test_buttonbar_remove_students_link(self):
        testassignment = mommy.make('core.Assignment')
        relatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.period)
        mock_cradmin_instance = self.__mockinstance_with_devilryrole('departmentadmin')

        def mock_reverse_url(appname, viewname, args, kwargs):
            return '/{}/{}/{}'.format(appname, kwargs.get('relatedexaminer_id'), viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            '/remove_groups_from_examiner/{}/INDEX'.format(relatedexaminer.id),
            mockresponse.selector
            .one('#devilry_admin_assignment_examinerdetails_button_remove_students')['href'])

    def test_buttonbar_remove_students_text(self):
        testassignment = mommy.make('core.Assignment')
        relatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Remove some or all students',
            mockresponse.selector
            .one('#devilry_admin_assignment_examinerdetails_button_remove_students').alltext_normalized)

    def test_groups_sanity(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.period)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            2,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_groups_only_where_is_examiner(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.period)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=testgroup)
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'relatedexaminer_id': relatedexaminer.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))
