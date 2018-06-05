import mock
import time
from django import test
from django.conf import settings
from django.contrib import messages
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Examiner
from devilry.devilry_admin.views.assignment.examiners import bulk_organize
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from unittest import skip


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

    def test_header_backlink_url(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mock_cradmin_instance = mock.MagicMock()

        def mock_reverse_url(appname, viewname, **kwargs):
            return '/{}/{}'.format(appname, viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                                          cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            '/examineroverview/INDEX',
            mockresponse.selector.one('.devilry-page-header-backlink')['href'])

    def test_buttons_sanity(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            3,
            mockresponse.selector.count(
                '#devilry_admin_assignment_examiners_bulk_organize_buttons .btn'))

    def test_buttonbar_random_link(self):
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

    def test_buttonbar_random_text(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Organize examiners randomly( Select students and '
            'randomly assign two or more examiners to those students )',
            mockresponse.selector
            .one('#devilry_admin_assignment_examiners_bulk_organize_button_random')
            .alltext_normalized)

    def test_buttonbar_manual_add_link(self):
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
            '/manual-add',
            mockresponse.selector
            .one('#devilry_admin_assignment_examiners_bulk_organize_button_manual_add')['href'])

    def test_buttonbar_manual_add_text(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Manually add examiners( Select students and add examiners to those students )',
            mockresponse.selector
            .one('#devilry_admin_assignment_examiners_bulk_organize_button_manual_add')
            .alltext_normalized)

    def test_buttonbar_manual_replace_link(self):
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
            '/manual-replace',
            mockresponse.selector
            .one('#devilry_admin_assignment_examiners_bulk_organize_button_manual_replace')['href'])

    def test_buttonbar_manual_replace_text(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Manually replace examiners( Select students and replace examiners for those students )',
            mockresponse.selector
            .one('#devilry_admin_assignment_examiners_bulk_organize_button_manual_replace')
            .alltext_normalized)

    def test_students_without_examiners_warning(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.Candidate', assignment_group__parentnode=testassignment)
        mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertTrue(mockresponse.selector.exists('#id_devilry_admin_assignment_bulk_organize_examiner'))
        self.assertEqual(
            mockresponse.selector.one('#id_devilry_admin_assignment_bulk_organize_examiner').alltext_normalized,
            'warning: There are still students on the assignment with no examiners assigned to them')

    def test_students_all_students_are_assigned_examiners_warning_not_rendered(self):
        testassignment = mommy.make('core.Assignment')
        assignment_group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=assignment_group)
        mommy.make('core.Examiner', related_examiner__period=testassignment.parentnode,
                   assignmentgroup=assignment_group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertFalse(mockresponse.selector.exists('#id_devilry_admin_assignment_bulk_organize_examiner'))


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
                '#div_id_selected_relatedexaminers .checkbox label')]
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

    def test_post_clears_existing(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer3 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer3,
                   assignmentgroup=testgroup1)
        self.assertEqual(1, Examiner.objects.count())
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
        self.assertFalse(Examiner.objects.filter(relatedexaminer=relatedexaminer3).exists())

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

    def test_post_evenly_distributed_symmetrical(self):
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
        testgroup9 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
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
                                           str(testgroup8.id), str(testgroup9.id)],
                        'selected_relatedexaminers': [str(relatedexaminer1.id),
                                                      str(relatedexaminer2.id),
                                                      str(relatedexaminer3.id)],
                    }
                })
            self.assertEqual(relatedexaminer1.examiner_set.count(), 3)
            self.assertEqual(relatedexaminer2.examiner_set.count(), 3)
            self.assertEqual(relatedexaminer3.examiner_set.count(), 3)

    def test_post_evenly_distributed_more_groups_than_examiners(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer3 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer4 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer5 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer6 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer7 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer8 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        for index in range(30):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                requestkwargs={
                    'data': {
                        'selected_items': [str(testgroup1.id), str(testgroup2.id),
                                           str(testgroup3.id)],
                        'selected_relatedexaminers': [str(relatedexaminer1.id),
                                                      str(relatedexaminer2.id),
                                                      str(relatedexaminer3.id),
                                                      str(relatedexaminer4.id),
                                                      str(relatedexaminer5.id),
                                                      str(relatedexaminer6.id),
                                                      str(relatedexaminer7.id),
                                                      str(relatedexaminer8.id)],
                    }
                })
            count_examiner1 = relatedexaminer1.examiner_set.count()
            count_examiner2 = relatedexaminer2.examiner_set.count()
            count_examiner3 = relatedexaminer3.examiner_set.count()
            count_examiner4 = relatedexaminer3.examiner_set.count()
            count_examiner5 = relatedexaminer3.examiner_set.count()
            count_examiner6 = relatedexaminer3.examiner_set.count()
            count_examiner7 = relatedexaminer3.examiner_set.count()
            count_examiner8 = relatedexaminer3.examiner_set.count()
            self.assertTrue(
                (count_examiner1 == 0 or count_examiner1 == 1) and
                (count_examiner2 == 0 or count_examiner2 == 1) and
                (count_examiner3 == 0 or count_examiner3 == 1) and
                (count_examiner4 == 0 or count_examiner4 == 1) and
                (count_examiner5 == 0 or count_examiner5 == 1) and
                (count_examiner6 == 0 or count_examiner6 == 1) and
                (count_examiner7 == 0 or count_examiner7 == 1) and
                (count_examiner8 == 0 or count_examiner8 == 1)
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
            bulk_organize.RandomOrganizeForm.invalid_students_selected_message,
            '')


class TestManualAddView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    NOTE: Much of the functionality for this view is tested in
    test_groupview_base.test_groupviewmixin.TestGroupViewMixin
    and test_basemultiselectview.TestBaseMultiselectView.
    """
    viewclass = bulk_organize.ManualAddView

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
            'Manually add examiners',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Manually add examiners',
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
            'Add selected examiners to selected students',
            mockresponse.selector.one('.django-cradmin-multiselect2-target-formfields .btn').alltext_normalized)

    def test_target_with_selected_items_title(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Selected students:',
            mockresponse.selector.one('.django-cradmin-multiselect2-target-title').alltext_normalized)

    def test_target_examiners_title(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Select examiners:*',
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
                '#div_id_selected_relatedexaminers .checkbox label')]
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
        self.assertEqual({relatedexaminer1, relatedexaminer2},
                         {examiner.relatedexaminer for examiner in testgroup1.examiners.all()})
        self.assertEqual({relatedexaminer1, relatedexaminer2},
                         {examiner.relatedexaminer for examiner in testgroup2.examiners.all()})
        self.assertEqual(4, Examiner.objects.count())

    def test_post_adds_to_existing(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer2,
                   assignmentgroup=testgroup)
        self.assertEqual(1, Examiner.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestkwargs={
                'data': {
                    'selected_items': [str(testgroup.id)],
                    'selected_relatedexaminers': [str(relatedexaminer1.id)],
                }
            })
        self.assertEqual({relatedexaminer1, relatedexaminer2},
                         {examiner.relatedexaminer for examiner in testgroup.examiners.all()})
        self.assertEqual(2, Examiner.objects.count())

    def test_post_does_not_add_duplicates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer1,
                   assignmentgroup=testgroup)
        self.assertEqual(1, Examiner.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestkwargs={
                'data': {
                    'selected_items': [str(testgroup.id)],
                    'selected_relatedexaminers': [str(relatedexaminer1.id)],
                }
            })
        self.assertEqual({relatedexaminer1},
                         {examiner.relatedexaminer for examiner in testgroup.examiners.all()})
        self.assertEqual(1, Examiner.objects.count())

    def test_post_no_examiners_selected(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        messagesmock = mock.MagicMock()
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestkwargs={
                'data': {
                    'selected_items': [str(testgroup.id)],
                    'selected_relatedexaminers': [],
                }
            })
        self.assertEqual(
                bulk_organize.ManualAddOrReplaceExaminersForm.selected_relatedexaminers_required_message,
                mockresponse.selector.one(
                        '#div_id_selected_relatedexaminers.has-error .help-block').alltext_normalized)
        messagesmock.add.assert_called_once_with(
            messages.ERROR,
            bulk_organize.ManualAddOrReplaceExaminersForm.selected_relatedexaminers_required_message,
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
            bulk_organize.ManualAddOrReplaceExaminersForm.invalid_students_selected_message,
            '')


class TestManualReplaceView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    NOTE: Much of the functionality for this view is tested in
    test_groupview_base.test_groupviewmixin.TestGroupViewMixin
    and test_basemultiselectview.TestBaseMultiselectView.
    """
    viewclass = bulk_organize.ManualReplaceView

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
            'Manually replace examiners',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Manually replace examiners',
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
            'Replace selected examiners with current examiners for selected students',
            mockresponse.selector.one('.django-cradmin-multiselect2-target-formfields .btn').alltext_normalized)

    def test_target_with_selected_items_title(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Selected students:',
            mockresponse.selector.one('.django-cradmin-multiselect2-target-title').alltext_normalized)

    def test_target_examiners_title(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Select examiners:*',
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
                '#div_id_selected_relatedexaminers .checkbox label')]
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
        self.assertEqual({relatedexaminer1, relatedexaminer2},
                         {examiner.relatedexaminer for examiner in testgroup1.examiners.all()})
        self.assertEqual({relatedexaminer1, relatedexaminer2},
                         {examiner.relatedexaminer for examiner in testgroup2.examiners.all()})
        self.assertEqual(4, Examiner.objects.count())

    def test_post_replaces_existing(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        relatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', period=testassignment.period)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer1,
                   assignmentgroup=testgroup)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer2,
                   assignmentgroup=testgroup)
        self.assertEqual(2, Examiner.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestkwargs={
                'data': {
                    'selected_items': [str(testgroup.id)],
                    'selected_relatedexaminers': [str(relatedexaminer1.id)],
                }
            })
        self.assertEqual({relatedexaminer1},
                         {examiner.relatedexaminer for examiner in testgroup.examiners.all()})
        self.assertEqual(1, Examiner.objects.count())

    def test_post_no_examiners_selected(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        messagesmock = mock.MagicMock()
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestkwargs={
                'data': {
                    'selected_items': [str(testgroup.id)],
                    'selected_relatedexaminers': [],
                }
            })
        self.assertEqual(
                bulk_organize.ManualAddOrReplaceExaminersForm.selected_relatedexaminers_required_message,
                mockresponse.selector.one(
                        '#div_id_selected_relatedexaminers.has-error .help-block').alltext_normalized)
        messagesmock.add.assert_called_once_with(
            messages.ERROR,
            bulk_organize.ManualAddOrReplaceExaminersForm.selected_relatedexaminers_required_message,
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
            bulk_organize.ManualAddOrReplaceExaminersForm.invalid_students_selected_message,
            '')


@skip('Skip tests, organize examiners by period tags')
class TestOrganizeByTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_organize.OrganizeByTagListbuilderView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_no_related_students(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtag = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testrelatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.parentnode)
        testperiodtag.relatedexaminers.add(testrelatedexaminer)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))

    def test_no_related_students_message_link(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtag = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testrelatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        testperiodtag.relatedstudents.add(testrelatedstudent)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-listbuilderlist-footer'))
        self.assertEquals(mockresponse.selector.one('.devilry-listbuilderlist-footer').alltext_normalized,
                          'Tags exist for the semester, but is missing either examiners, students or both. '
                          'Manage tags.')

    def test_no_related_examiners(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtag = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testrelatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        testperiodtag.relatedstudents.add(testrelatedstudent)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))

    def test_no_related_examiners_message_link(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtag = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testrelatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        testperiodtag.relatedstudents.add(testrelatedstudent)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-listbuilderlist-footer'))
        self.assertEquals(mockresponse.selector.one('.devilry-listbuilderlist-footer').alltext_normalized,
                          'Tags exist for the semester, but is missing either examiners, students or both. '
                          'Manage tags.')

    def test_no_period_tags_message_link(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-listbuilderlist-footer'))
        self.assertEquals(mockresponse.selector.one('.devilry-listbuilderlist-footer').alltext_normalized,
                          'No tags registered on the semester. If you add tags, '
                          'you can organize examiners and students based on the tags. Add semester tags.')

    def test_no_candidates_in_groups(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtag1 = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testperiodtag2 = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testrelatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        testrelatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.parentnode)
        testperiodtag1.relatedstudents.add(testrelatedstudent)
        testperiodtag1.relatedexaminers.add(testrelatedexaminer)
        testperiodtag2.relatedstudents.add(testrelatedstudent)
        testperiodtag2.relatedexaminers.add(testrelatedexaminer)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))

    def test_no_candidates_in_groups_where_relatedstudent_is_registered_on_tag(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtag = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        testrelatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        testrelatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.parentnode)
        testperiodtag.relatedstudents.add(testrelatedstudent)
        testperiodtag.relatedexaminers.add(testrelatedexaminer)
        mommy.make('core.Candidate', assignment_group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))

    def test_candidates_in_groups(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtag1 = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testrelatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        testrelatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.parentnode)
        testperiodtag1.relatedstudents.add(testrelatedstudent)
        testperiodtag1.relatedexaminers.add(testrelatedexaminer)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=testrelatedstudent)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertTrue(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))
        self.assertTrue(mockresponse.selector.one('.django-cradmin-listbuilder-itemvalue'))

    def test_post(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtag = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testrelatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user__shortname='sa')
        testrelatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.parentnode)

        # add relatedstudent and relatedexaminer to tag
        testperiodtag.relatedstudents.add(testrelatedstudent)
        testperiodtag.relatedexaminers.add(testrelatedexaminer)
        mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent=testrelatedstudent)
        mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent=testrelatedstudent)

        self.mock_http302_postrequest(
            cradmin_role=testassignment
        )

        examiners = Examiner.objects.all()
        group1 = AssignmentGroup.objects.get(id=testgroup1.id)
        group2 = AssignmentGroup.objects.get(id=testgroup2.id)
        self.assertEquals(examiners.count(), 2)
        self.assertEquals(examiners[0].relatedexaminer, testrelatedexaminer)
        self.assertEquals(examiners[1].relatedexaminer, testrelatedexaminer)
        self.assertIn(examiners[0], group1.examiners.all())
        self.assertIn(examiners[1], group2.examiners.all())

    def test_post_examiner_in_unrelated_group_is_not_deleted(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtag = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testrelatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode, user__shortname='sa')
        testrelatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.parentnode)

        # add relatedstudent and relatedexaminer to tag
        testperiodtag.relatedstudents.add(testrelatedstudent)
        testperiodtag.relatedexaminers.add(testrelatedexaminer)

        testexaminer_in_another_group = mommy.make('core.Examiner', relatedexaminer=testrelatedexaminer)
        testcandidate = mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=testrelatedstudent)

        self.mock_http302_postrequest(
            cradmin_role=testassignment
        )

        examiners = Examiner.objects.all()
        group = AssignmentGroup.objects.get(id=testgroup.id)
        self.assertEquals(examiners.count(), 2)
        self.assertIn(testcandidate, group.candidates.all())
        self.assertNotIn(testexaminer_in_another_group, group.examiners.all())
        self.assertEquals(group.examiners.all().count(), 1)

    def test_examiner_and_candidate_already_in_group(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtag = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testrelatedexaminer = mommy.make('core.RelatedExaminer', period=testassignment.parentnode)
        testrelatedstudent = mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=testrelatedexaminer)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=testrelatedstudent)
        testperiodtag.relatedexaminers.add(testrelatedexaminer)
        testperiodtag.relatedstudents.add(testrelatedstudent)
        self.mock_http302_postrequest(
            cradmin_role=testassignment
        )

    def test_post_sanity_multiple_tags(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtags = mommy.make('core.PeriodTag', period=testassignment.parentnode, _quantity=5)
        testrelatedstudents = mommy.make('core.RelatedStudent', period=testassignment.parentnode, _quantity=30)
        testrelatedexaminers = mommy.make('core.RelatedExaminer', period=testassignment.parentnode, _quantity=3)

        for periodtag in testperiodtags:
            for relatedstudent in testrelatedstudents:
                periodtag.relatedstudents.add(relatedstudent)
                mommy.make('core.Candidate', assignment_group__parentnode=testassignment, relatedstudent=relatedstudent)
            for relatedexaminer in testrelatedexaminers:
                periodtag.relatedexaminers.add(relatedexaminer)
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        with self.assertNumQueries(6):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                requestuser=requestuser
            )
        examiners = Examiner.objects.all()
        self.assertEquals(examiners.count(), 450)

    def test_get_query_count(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testperiodtag1 = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testperiodtag2 = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testperiodtag3 = mommy.make('core.PeriodTag', period=testassignment.parentnode)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testrelatedstudent1 = mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        testrelatedstudent2 = mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        testrelatedstudent3 = mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        testrelatedstudent4 = mommy.make('core.RelatedStudent', period=testassignment.parentnode)
        testrelatedexaminer1 = mommy.make('core.RelatedExaminer', period=testassignment.parentnode)
        testrelatedexaminer2 = mommy.make('core.RelatedExaminer', period=testassignment.parentnode)
        testrelatedexaminer3 = mommy.make('core.RelatedExaminer', period=testassignment.parentnode)

        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=testrelatedstudent1)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=testrelatedstudent2)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=testrelatedstudent3)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=testrelatedstudent4)
        testperiodtag1.relatedstudents.add(testrelatedstudent1, testrelatedstudent2, testrelatedstudent3,
                                           testrelatedstudent4)
        testperiodtag1.relatedexaminers.add(testrelatedexaminer1, testrelatedexaminer2, testrelatedexaminer3)
        testperiodtag2.relatedstudents.add(testrelatedstudent1, testrelatedstudent2, testrelatedstudent3,
                                           testrelatedstudent4)
        testperiodtag2.relatedexaminers.add(testrelatedexaminer1, testrelatedexaminer2, testrelatedexaminer3)
        testperiodtag3.relatedstudents.add(testrelatedstudent1, testrelatedstudent2, testrelatedstudent3,
                                           testrelatedstudent4)
        testperiodtag3.relatedexaminers.add(testrelatedexaminer1, testrelatedexaminer2, testrelatedexaminer3)

        with self.assertNumQueries(7):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment
            )
