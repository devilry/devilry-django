import mock
from django import test
from django.contrib import messages
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import Examiner
from devilry.devilry_admin.views.assignment.examiners import bulk_organize
from devilry.devilry_admin.views.assignment.students.groupview_base import SelectedGroupsForm


class TestSelectMethodView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_organize.SelectMethodView

    def test_title(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertIn(
            'How would you like to bulk-organize your examiners?',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'How would you like to bulk-organize your examiners?',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_buttons_sanity(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            1,
            mockresponse.selector.count(
                '#devilry_admin_assignment_examiners_bulk_organize_buttons .btn'))

    def test_buttonbar_organize_examiners_link(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.RelatedExaminer', period=testassignment.period)
        mock_cradmin_app = mock.MagicMock()

        def mock_reverse_url(viewname, *args, **kwargs):
            return '/{}'.format(viewname)

        mock_cradmin_app.reverse_appurl = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_app=mock_cradmin_app)
        self.assertEqual(
            '/random',
            mockresponse.selector
            .one('#devilry_admin_assignment_examiners_bulk_organize_button_random')['href'])

    def test_buttonbar_organize_examiners_text(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Organize examiners randomly( Select students and '
            'randomly assign two or more examiners to those students )',
            mockresponse.selector
            .one('#devilry_admin_assignment_examiners_bulk_organize_button_random')
            .alltext_normalized)


class TestRandomView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    NOTE: Much of the functionality for this view is tested in
    test_groupview_base.test_groupviewmixin.TestGroupViewMixin
    and test_basemultiselectview.TestBaseMultiselectView.
    """
    viewclass = bulk_organize.RandomView

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertIn(
            'Organize examiners randomly',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Organize examiners randomly',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_groups_sanity(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.AssignmentGroup', parentnode=testassignment, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            3,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_submit_button_text(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Randomly assign selected students to selected examiners',
            mockresponse.selector.one('.django-cradmin-multiselect2-target-formfields .btn').alltext_normalized)

    def test_target_with_selected_items_title(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Select at least two students:',
            mockresponse.selector.one('.django-cradmin-multiselect2-target-title').alltext_normalized)

    def test_target_examiners_title(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Select at least two examiners:',
            mockresponse.selector.one('#div_id_selected_relatedexaminers .control-label ').alltext_normalized)

    def test_target_examiners_values(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        values = [element['value']
                  for element in mockresponse.selector.list('input[name="selected_relatedexaminers"]')]
        self.assertEqual(
            {str(relatedexaminer1.id), str(relatedexaminer2.id)},
            set(values))

    def test_target_examiners_only_from_period(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        mommy.make('core.RelatedExaminer')  # Not in the same period as testassignment
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        values = [element['value']
                  for element in mockresponse.selector.list('input[name="selected_relatedexaminers"]')]
        self.assertEqual(
            {str(relatedexaminer1.id), str(relatedexaminer2.id)},
            set(values))

    def test_target_examiners_labels(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.RelatedExaminer', period=testassignment.period,
                   user__fullname='Examiner One')
        mommy.make('core.RelatedExaminer', period=testassignment.period,
                   user__shortname='examiner2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        labels = [
            element.alltext_normalized
            for element in mockresponse.selector.list(
                '#div_id_selected_relatedexaminers label.checkbox')]
        self.assertEqual(
            {'Examiner One', 'examiner2'},
            set(labels))

    def test_post_ok(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        self.assertEqual(0, Examiner.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestkwargs={
                'data': {
                    'selected_items': [str(testgroup1.id), str(testgroup2.id)],
                    'selected_relatedexaminers': [str(relatedexaminer1.id), str(relatedexaminer2.id)],
                }
            })
        self.assertEqual(2, Examiner.objects.count())

    def test_post_evenly_distributed(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer3 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup5 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup6 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup7 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup8 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        for index in range(30):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                requestkwargs={
                    'data': {
                        'selected_items': [str(testgroup1.id), str(testgroup2.id),
                                           str(testgroup3.id), str(testgroup4.id),
                                           str(testgroup5.id), str(testgroup5.id),
                                           str(testgroup6.id), str(testgroup7.id),
                                           str(testgroup8.id)],
                        'selected_relatedexaminers': [str(relatedexaminer1.id),
                                                      str(relatedexaminer2.id),
                                                      str(relatedexaminer3.id)],
                    }
                })
            count_examiner1 = relatedexaminer1.examiner_set.count()
            count_examiner2 = relatedexaminer2.examiner_set.count()
            count_examiner3 = relatedexaminer3.examiner_set.count()
            self.assertTrue(
                (count_examiner1 == 2 and count_examiner2 == 3 and count_examiner3 == 3) or
                (count_examiner1 == 3 and count_examiner2 == 2 and count_examiner3 == 3) or
                (count_examiner1 == 3 and count_examiner2 == 3 and count_examiner3 == 2)
            )

    def test_post_less_than_two_examiners(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        messagesmock = mock.MagicMock()
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestkwargs={
                'data': {
                    'selected_items': [str(testgroup1.id), str(testgroup2.id)],
                    'selected_relatedexaminers': [str(relatedexaminer1.id)],
                }
            })
        self.assertEqual(
                bulk_organize.RandomOrganizeForm.selected_relatedexaminers_invalid_choice_message,
                mockresponse.selector.one(
                        '#div_id_selected_relatedexaminers.has-error .help-block').alltext_normalized)
        messagesmock.add.assert_called_once_with(
            messages.ERROR,
            bulk_organize.RandomOrganizeForm.selected_relatedexaminers_invalid_choice_message,
            '')

    def test_post_invalid_groups(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        testgroup1 = mommy.make('core.AssignmentGroup')  # Not within the assignment
        messagesmock = mock.MagicMock()
        self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestkwargs={
                'data': {
                    'selected_items': [str(testgroup1.id)],
                    'selected_relatedexaminers': [str(relatedexaminer1.id), str(relatedexaminer2.id)],
                }
            })
        messagesmock.add.assert_called_once_with(
            messages.ERROR,
            SelectedGroupsForm.invalid_students_selected_message,
            '')
