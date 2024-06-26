import datetime

import htmls
from unittest import mock
from django import forms
from django.contrib import messages
from django.http import Http404
from django.test import TestCase
from django.utils import timezone
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core.models import AssignmentGroup, Candidate
from devilry.apps.core.baker_recipes import ACTIVE_PERIOD_START
from devilry.devilry_admin.views.assignment.students import replace_groups
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories
from devilry.devilry_group.models import FeedbackSet


class TestChooseMethod(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = replace_groups.ChooseMethod

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_redirect_if_assignment_is_published(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() - datetime.timedelta(days=2))
        mock_cradmin_instance = mock.MagicMock()
        messagesmock = mock.MagicMock()
        self.mock_http302_getrequest(
            cradmin_role=testassignment,
            cradmin_instance=mock_cradmin_instance,
            messagesmock=messagesmock)
        mock_cradmin_instance.rolefrontpage_url.assert_called_once_with()
        messagesmock.add.assert_called_once_with(
            messages.ERROR, self.viewclass.published_assignment_error_message, '')

    def test_title(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2),
                                    long_name='Assignment One')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertIn(
            'Replace students on Assignment One',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Replace students',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_choices_sanity(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            3,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue a'))

    def __mock_reverse_appurl(self):
        def reverse_appurl(viewname, args, kwargs):
            return '/{}/args={},kwargs={}'.format(viewname, args, kwargs)
        return reverse_appurl

    def test_choice_relatedstudents_url(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockapp = mock.MagicMock()
        mockapp.reverse_appurl = self.__mock_reverse_appurl()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_app=mockapp
        )
        self.assertEqual(
            "/confirm/args=(),kwargs={'selected_students': 'relatedstudents'}",
            mockresponse.selector.one(
                '#devilry_admin_create_groups_choosemethod_relatedstudents_link')['href'])

    def test_choice_relatedstudents_label(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2),
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'All students',
            mockresponse.selector.one(
                '#devilry_admin_create_groups_choosemethod_relatedstudents_link').alltext_normalized)

    def test_choice_manual_select_value(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockapp = mock.MagicMock()
        mockapp.reverse_appurl = self.__mock_reverse_appurl()
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_app=mockapp
        )
        self.assertEqual(
            "/manual-select/args=(),kwargs={}",
            mockresponse.selector.one(
                '#devilry_admin_create_groups_choosemethod_manualselect_link')['href'])

    def test_choice_manual_select_label(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Select manually',
            mockresponse.selector.one(
                '#devilry_admin_create_groups_choosemethod_manualselect_link').alltext_normalized)

    def test_choices_does_not_include_current_assignment(self):
        testperiod = baker.make('core.Period')
        otherassignment = baker.make('core.Assignment', parentnode=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            5,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue a'))
        self.assertFalse(
            mockresponse.selector.exists('#devilry_admin_create_groups_choosemethod_assignment_{}'.format(
                testassignment.pk)))
        self.assertTrue(
            mockresponse.selector.exists('#devilry_admin_create_groups_choosemethod_assignment_{}'.format(
                otherassignment.pk)))

    def test_other_assignment_rending(self):
        testperiod = baker.make('core.Period')
        otherassignment = baker.make('core.Assignment', parentnode=testperiod,
                                     short_name='otherassignment')
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'All students',
            mockresponse.selector.one('#devilry_admin_create_groups_choosemethod_assignment_{}_all_link'.format(
                otherassignment.pk)).alltext_normalized)
        self.assertEqual(
            'Students with passing grade',
            mockresponse.selector.one('#devilry_admin_create_groups_choosemethod_assignment_{}_passing_link'.format(
                otherassignment.pk)).alltext_normalized)

    def test_other_assignments_ordering(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        assignment1 = baker.make('core.Assignment', parentnode=testperiod,
                                 publishing_time=ACTIVE_PERIOD_START + datetime.timedelta(days=1))
        assignment2 = baker.make('core.Assignment', parentnode=testperiod,
                                 publishing_time=ACTIVE_PERIOD_START + datetime.timedelta(days=2))
        assignment3 = baker.make('core.Assignment', parentnode=testperiod,
                                 publishing_time=ACTIVE_PERIOD_START + datetime.timedelta(days=3))
        assignment4 = baker.make('core.Assignment', parentnode=testperiod,
                                 publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment4)
        assignmentboxes_dom_ids = [
            element['id']
            for element in mockresponse.selector.list('.devilry-admin-create-groups-choosemethod-assignment')]
        self.assertEqual(
            [
                'devilry_admin_create_groups_choosemethod_assignment_{}'.format(assignment3.id),
                'devilry_admin_create_groups_choosemethod_assignment_{}'.format(assignment2.id),
                'devilry_admin_create_groups_choosemethod_assignment_{}'.format(assignment1.id),
            ],
            assignmentboxes_dom_ids
        )


class TestConfirmView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = replace_groups.ConfirmView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_redirect_if_assignment_is_published(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() - datetime.timedelta(days=2))
        mock_cradmin_instance = mock.MagicMock()
        messagesmock = mock.MagicMock()
        self.mock_http302_getrequest(
            cradmin_role=testassignment,
            cradmin_instance=mock_cradmin_instance,
            messagesmock=messagesmock)
        mock_cradmin_instance.rolefrontpage_url.assert_called_once_with()
        messagesmock.add.assert_called_once_with(
            messages.ERROR, self.viewclass.published_assignment_error_message, '')

    def test_title(self):
        testassignment = baker.make('core.Assignment', long_name='Assignment One',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_RELATEDSTUDENTS})
        self.assertIn(
            'Confirm that you want to remove the current students on Assignment One '
            'and replace them with the students shown below',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = baker.make('core.Assignment', long_name='Assignment One',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_RELATEDSTUDENTS})
        self.assertEqual(
            'Confirm that you want to remove the current students on Assignment One '
            'and replace them with the students shown below',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_get_subheader_selected_students_relateadstudents(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2),
                                    parentnode__parentnode__short_name='testsubject',
                                    parentnode__short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_RELATEDSTUDENTS})
        self.assertEqual(
            'All students on testsubject.testperiod',
            mockresponse.selector.one(
                '#devilry_admin_create_groups_confirm_selected_student_label').alltext_normalized)

    def test_get_subheader_selected_students_all_on_assignment(self):
        testperiod = baker.make('core.Period')
        otherassignment = baker.make('core.Assignment',
                                     long_name='Assignment One',
                                     parentnode=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestkwargs={'data': {'assignment': otherassignment.id}},
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_ALL_ON_ASSIGNMENT})
        self.assertEqual(
            'All students on Assignment One',
            mockresponse.selector.one(
                '#devilry_admin_create_groups_confirm_selected_student_label').alltext_normalized)

    def test_get_subheader_selected_students_passing_grade_on_assignment(self):
        testperiod = baker.make('core.Period')
        otherassignment = baker.make('core.Assignment',
                                     long_name='Assignment One',
                                     parentnode=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestkwargs={'data': {'assignment': otherassignment.id}},
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_PASSING_GRADE_ON_ASSIGNMENT})
        self.assertEqual(
            'Students with passing grade on Assignment One',
            mockresponse.selector.one(
                '#devilry_admin_create_groups_confirm_selected_student_label').alltext_normalized)

    def test_get_render_submitbutton(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent', period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_RELATEDSTUDENTS})
        self.assertEqual(
            'Add students',
            mockresponse.selector.one(
                '#devilry_admin_create_groups_confirm_form button[name="add_students"]').alltext_normalized
        )

    def test_get_render_form_selected_items_selected_students_relatedstudents(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = baker.make('core.RelatedStudent', period=testperiod)
        relatedstudent2 = baker.make('core.RelatedStudent', period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_RELATEDSTUDENTS})
        selected_relatedstudent_ids = [
            element['value']
            for element in mockresponse.selector.list(
                '#devilry_admin_create_groups_confirm_form input[name=selected_items]')]
        self.assertEqual(
            {str(relatedstudent1.id), str(relatedstudent2.id)},
            set(selected_relatedstudent_ids))

    def test_get_render_form_selected_items_selected_students_all_on_assignment(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = baker.make('core.RelatedStudent', period=testperiod)
        relatedstudent2 = baker.make('core.RelatedStudent', period=testperiod)
        baker.make('core.RelatedStudent', period=testperiod)
        otherassignment = baker.make('core.Assignment', parentnode=testperiod)
        baker.make('core.Candidate',
                   relatedstudent=relatedstudent1,
                   assignment_group__parentnode=otherassignment)
        baker.make('core.Candidate',
                   relatedstudent=relatedstudent2,
                   assignment_group__parentnode=otherassignment)

        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestkwargs={
                'data': {'assignment': otherassignment.id}
            },
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_ALL_ON_ASSIGNMENT})
        selected_relatedstudent_ids = [
            element['value']
            for element in mockresponse.selector.list(
                '#devilry_admin_create_groups_confirm_form input[name=selected_items]')]
        self.assertEqual(
            {str(relatedstudent1.id), str(relatedstudent2.id)},
            set(selected_relatedstudent_ids))

    def test_get_render_form_selected_items_selected_students_passing_grade_on_assignment(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = baker.make('core.RelatedStudent', period=testperiod)
        relatedstudent2 = baker.make('core.RelatedStudent', period=testperiod)
        baker.make('core.RelatedStudent', period=testperiod)
        otherassignment = baker.make('core.Assignment', parentnode=testperiod,
                                     passing_grade_min_points=1)
        candidate1 = baker.make('core.Candidate',
                                relatedstudent=relatedstudent1,
                                assignment_group__parentnode=otherassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=candidate1.assignment_group,
            grading_points=1)
        baker.make('core.Candidate',
                   relatedstudent=relatedstudent2,
                   assignment_group__parentnode=otherassignment)

        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestkwargs={
                'data': {'assignment': otherassignment.id}
            },
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_PASSING_GRADE_ON_ASSIGNMENT})
        selected_relatedstudent_ids = [
            element['value']
            for element in mockresponse.selector.list(
                '#devilry_admin_create_groups_confirm_form input[name=selected_items]')]
        self.assertEqual(
            {str(relatedstudent1.id)},
            set(selected_relatedstudent_ids))

    def test_get_no_relatedstudents_matching_query(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_RELATEDSTUDENTS})
        self.assertEqual(
            'No students matching your selection found.',
            mockresponse.selector.one(
                '.devilry-admin-create-groups-confirm-no-students').alltext_normalized)

    def test_get_selected_students_relateadstudents(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent',
                   user__fullname='Match User',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__fullname='Other User',
                   period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_RELATEDSTUDENTS})
        self.assertEqual(
            2,
            mockresponse.selector.count('.devilry-admin-listbuilder-relatedstudent-readonlyitemvalue'))

    def test_get_selected_students_all_on_assignment_invalid_assignment_id(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent', period=testperiod)
        otherassignment = baker.make('core.Assignment')  # Not in testperiod!
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        with self.assertRaisesMessage(Http404, 'Invalid assignment_id'):
            self.mock_getrequest(
                cradmin_role=testassignment,
                viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_ALL_ON_ASSIGNMENT},
                requestkwargs={
                    'data': {'assignment': otherassignment.id}
                })

    def test_get_selected_students_all_on_assignment(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        relatedstudent2 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        relatedstudent3 = baker.make('core.RelatedStudent',
                                     user__fullname='User that is not on the other assignment',
                                     period=testperiod)
        otherassignment = baker.make('core.Assignment', parentnode=testperiod)
        baker.make('core.Candidate',
                   relatedstudent=relatedstudent1,
                   assignment_group__parentnode=otherassignment)
        baker.make('core.Candidate',
                   relatedstudent=relatedstudent2,
                   assignment_group__parentnode=otherassignment)

        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_ALL_ON_ASSIGNMENT},
            requestkwargs={
                'data': {'assignment': otherassignment.id}
            })
        self.assertEqual(
            2,
            mockresponse.selector.count('.devilry-admin-listbuilder-relatedstudent-readonlyitemvalue'))
        self.assertNotContains(mockresponse.response, relatedstudent3.user.fullname)

    def test_get_selected_students_passing_grade_on_assignment_invalid_assignment_id(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent', period=testperiod)
        otherassignment = baker.make('core.Assignment')  # Not in testperiod!
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        with self.assertRaisesMessage(Http404, 'Invalid assignment_id'):
            self.mock_getrequest(
                cradmin_role=testassignment,
                viewkwargs={
                    'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_PASSING_GRADE_ON_ASSIGNMENT},
                requestkwargs={
                    'data': {'assignment': otherassignment.id}
                })

    def test_get_selected_students_passing_grade_on_assignment(self):
        testperiod = baker.make('core.Period')
        otherassignment = baker.make('core.Assignment',
                                     parentnode=testperiod,
                                     passing_grade_min_points=1)

        relatedstudent1 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        candidate1 = baker.make('core.Candidate',
                                relatedstudent=relatedstudent1,
                                assignment_group__parentnode=otherassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=candidate1.assignment_group,
            grading_points=1)

        relatedstudent2 = baker.make('core.RelatedStudent',
                                     user__fullname='User that is not candidate',
                                     period=testperiod)

        relatedstudent3 = baker.make('core.RelatedStudent',
                                     user__fullname='User that did not pass',
                                     period=testperiod)
        candidate3 = baker.make('core.Candidate',
                                relatedstudent=relatedstudent3,
                                assignment_group__parentnode=otherassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=candidate3.assignment_group,
            grading_points=0)

        relatedstudent4 = baker.make('core.RelatedStudent',
                                     user__fullname='User that is not on the other assignment',
                                     period=testperiod)

        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'selected_students': replace_groups.ConfirmView.SELECTED_STUDENTS_PASSING_GRADE_ON_ASSIGNMENT},
            requestkwargs={
                'data': {'assignment': otherassignment.id}
            })
        self.assertEqual(
            1,
            mockresponse.selector.count('.devilry-admin-listbuilder-relatedstudent-readonlyitemvalue'))
        self.assertNotContains(mockresponse.response, relatedstudent2.user.fullname)
        self.assertNotContains(mockresponse.response, relatedstudent3.user.fullname)
        self.assertNotContains(mockresponse.response, relatedstudent4.user.fullname)

    def test_post_ok_creates_groups(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        relatedstudent2 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        relatedstudent3 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        self.assertEqual(0, AssignmentGroup.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'selected_items': [
                        relatedstudent1.id,
                        relatedstudent2.id,
                        relatedstudent3.id,
                    ]
                }
            }
        )
        # Note: We only need a sanity tests here - the real tests are
        # in the tests for AssignmentGroup.objects.bulk_create_groups()
        self.assertEqual(3, AssignmentGroup.objects.count())
        self.assertEqual(3, Candidate.objects.count())
        self.assertEqual(3, FeedbackSet.objects.count())
        first_group = AssignmentGroup.objects.first()
        self.assertEqual(1, first_group.candidates.count())
        self.assertEqual(1, first_group.feedbackset_set.count())

    def test_post_ok_redirect(self):
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        self.assertEqual(0, AssignmentGroup.objects.count())
        mock_cradmin_instance = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=mock_cradmin_instance,
            requestkwargs={
                'data': {
                    'selected_items': [
                        relatedstudent.id,
                    ]
                }
            }
        )
        mock_cradmin_instance.appindex_url.assert_called_once_with('studentoverview')

    def test_post_relatedstudent_already_on_assignment(self):
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testcandidate = baker.make('core.Candidate',
                                   relatedstudent=relatedstudent,
                                   assignment_group=testgroup)
        self.assertEqual(1, AssignmentGroup.objects.count())
        messagesmock = mock.MagicMock()
        mock_cradmin_instance = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_instance=mock_cradmin_instance,
            requestkwargs={
                'data': {
                    'selected_items': [
                        relatedstudent.id
                    ]
                }
            },
        )
        mock_cradmin_instance.appindex_url.assert_called_once_with('studentoverview')
        self.assertEqual(1, AssignmentGroup.objects.count())
        created_group = AssignmentGroup.objects.first()
        self.assertNotEqual(testgroup, created_group)
        self.assertNotEqual(testcandidate, created_group.candidates.first())

    def test_post_relatedstudent_not_relatedstudent_on_period(self):
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent',
                                    user__shortname='userb@example.com')
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        self.assertEqual(0, AssignmentGroup.objects.count())
        messagesmock = mock.MagicMock()
        mockapp = mock.MagicMock()
        mockapp.reverse_appindexurl.return_value = '/appindex'
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_app=mockapp,
            requestkwargs={
                'data': {
                    'selected_items': [
                        relatedstudent.id
                    ]
                }
            },
        )
        mockapp.reverse_appindexurl.assert_called_once_with()
        self.assertEqual('/appindex', mockresponse.response['Location'])
        self.assertEqual(0, AssignmentGroup.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.ERROR,
            replace_groups.ConfirmView.form_invalid_message,
            '')


class TestRelatedStudentMultiselectTarget(TestCase):
    def test_with_items_title(self):
        selector = htmls.S(replace_groups.RelatedStudentMultiselectTarget(
                form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual(
            'Replace students',
            selector.one('button[type="submit"]').alltext_normalized)


class TestManualSelectStudentsView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = replace_groups.ManualSelectStudentsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_redirect_if_assignment_is_published(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() - datetime.timedelta(days=2))
        mock_cradmin_instance = mock.MagicMock()
        messagesmock = mock.MagicMock()
        self.mock_http302_getrequest(
            cradmin_role=testassignment,
            cradmin_instance=mock_cradmin_instance,
            messagesmock=messagesmock)
        mock_cradmin_instance.rolefrontpage_url.assert_called_once_with()
        messagesmock.add.assert_called_once_with(
            messages.ERROR, self.viewclass.published_assignment_error_message, '')

    def test_title(self):
        testassignment = baker.make('core.Assignment',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2),
                                    short_name='testassignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertIn(
            'Select the students you want to add to testsubject.testperiod.testassignment',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = baker.make('core.Assignment', long_name='Assignment One',
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Select the students you want to add to Assignment One',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_no_relatedstudents(self):
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'No students found.',
            mockresponse.selector.one(
                '.devilry-admin-create-groups-manual-select-no-relatedstudents-message').alltext_normalized)

    def test_relatedstudent_not_in_assignment_period_excluded(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent')
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_relatedstudent_in_assignment_period_included(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent',
                   period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_relatedstudent_with_candidate_on_assignment_is_included(self):
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        baker.make('core.Candidate',
                   relatedstudent=relatedstudent,
                   assignment_group__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_render_relatedstudent_sanity(self):
        # This is tested in detail in the tests for
        # devilry.devilry_admin.cradminextensions.multiselect2.multiselect2_relatedstudent.ItemValue
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent',
                   user__shortname='testuser',
                   user__fullname='Test User',
                   period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Test User(testuser)',
            mockresponse.selector.one(
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_render_search(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent',
                   user__shortname='testuser',
                   user__fullname='Match User',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__fullname='Other User',
                   period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'search-match'}
        )
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))
        self.assertEqual(
            'Match User(testuser)',
            mockresponse.selector.one(
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_render_orderby_default(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent',
                   user__shortname='userb@example.com',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='x',
                   user__fullname='UserA',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='userc',
                   period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment)
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list(
                      '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(
            ['UserA(x)', 'userb@example.com', 'userc'],
            titles)

    def test_render_orderby_name_descending(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent',
                   user__shortname='userb@example.com',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='x',
                   user__fullname='UserA',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='userc',
                   period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-name_descending'})
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list(
                      '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(
            ['userc', 'userb@example.com', 'UserA(x)'],
            titles)

    def test_render_orderby_lastname_ascending(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent',
                   user__shortname='userb@example.com',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='x',
                   user__fullname='User Aaa',
                   user__lastname='Aaa',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='y',
                   user__fullname='User ccc',
                   user__lastname='ccc',
                   period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-lastname_ascending'})
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list(
                      '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(
            ['userb@example.com', 'User Aaa(x)', 'User ccc(y)'],
            titles)

    def test_render_orderby_lastname_descending(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent',
                   user__shortname='userb@example.com',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='x',
                   user__fullname='User Aaa',
                   user__lastname='Aaa',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='y',
                   user__fullname='User ccc',
                   user__lastname='ccc',
                   period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-lastname_descending'})
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list(
                      '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(
            ['User ccc(y)', 'User Aaa(x)', 'userb@example.com'],
            titles)

    def test_render_orderby_shortname_ascending(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent',
                   user__shortname='userb@example.com',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='usera@example.com',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='userc@example.com',
                   period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-shortname_ascending'})
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list(
                      '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(
            ['usera@example.com', 'userb@example.com', 'userc@example.com'],
            titles)

    def test_render_orderby_shortname_descending(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent',
                   user__shortname='userb@example.com',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='usera@example.com',
                   period=testperiod)
        baker.make('core.RelatedStudent',
                   user__shortname='userc@example.com',
                   period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-shortname_descending'})
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list(
                      '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(
            ['userc@example.com', 'userb@example.com', 'usera@example.com'],
            titles)

    def test_post_ok_creates_groups(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        relatedstudent2 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        relatedstudent3 = baker.make('core.RelatedStudent',
                                     period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        self.assertEqual(0, AssignmentGroup.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'selected_items': [
                        relatedstudent1.id,
                        relatedstudent2.id,
                        relatedstudent3.id,
                    ]
                }
            }
        )
        # Note: We only need a sanity tests here - the real tests are
        # in the tests for AssignmentGroup.objects.bulk_create_groups()
        self.assertEqual(3, AssignmentGroup.objects.count())
        self.assertEqual(3, Candidate.objects.count())
        self.assertEqual(3, FeedbackSet.objects.count())
        first_group = AssignmentGroup.objects.first()
        self.assertEqual(1, first_group.candidates.count())
        self.assertEqual(1, first_group.feedbackset_set.count())

    def test_post_ok_redirect(self):
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        self.assertEqual(0, AssignmentGroup.objects.count())
        mock_cradmin_instance = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=mock_cradmin_instance,
            requestkwargs={
                'data': {
                    'selected_items': [
                        relatedstudent.id,
                    ]
                }
            }
        )
        mock_cradmin_instance.appindex_url.assert_called_once_with('studentoverview')

    def test_post_relatedstudent_already_on_assignment(self):
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testcandidate = baker.make('core.Candidate',
                                   relatedstudent=relatedstudent,
                                   assignment_group=testgroup)
        self.assertEqual(1, AssignmentGroup.objects.count())
        messagesmock = mock.MagicMock()
        mock_cradmin_instance = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_instance=mock_cradmin_instance,
            requestkwargs={
                'data': {
                    'selected_items': [
                        relatedstudent.id
                    ]
                }
            },
        )
        mock_cradmin_instance.appindex_url.assert_called_once_with('studentoverview')
        self.assertEqual(1, AssignmentGroup.objects.count())
        created_group = AssignmentGroup.objects.first()
        self.assertNotEqual(testgroup, created_group)
        self.assertNotEqual(testcandidate, created_group.candidates.first())

    def test_post_relatedstudent_not_relatedstudent_on_period(self):
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent',
                                    user__shortname='userb@example.com')
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                    publishing_time=timezone.now() + datetime.timedelta(days=2))
        self.assertEqual(0, AssignmentGroup.objects.count())
        messagesmock = mock.MagicMock()
        mockapp = mock.MagicMock()
        mockapp.reverse_appurl.return_value = '/manual-select'
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_app=mockapp,
            requestkwargs={
                'data': {
                    'selected_items': [
                        relatedstudent.id
                    ]
                }
            },
        )
        mockapp.reverse_appurl.assert_called_once_with('manual-select')
        self.assertEqual('/manual-select', mockresponse.response['Location'])
        self.assertEqual(0, AssignmentGroup.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.ERROR,
            replace_groups.ManualSelectStudentsView.form_invalid_message,
            '')
