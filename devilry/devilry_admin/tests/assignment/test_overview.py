from datetime import datetime, timedelta
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.apps.core.mommy_recipes import assignment_activeperiod_end
from devilry.apps.core import models as coremodels
from devilry.devilry_admin.views.assignment import overview
from devilry.project.develop.testhelpers.corebuilder import AssignmentBuilder, UserBuilder, PeriodBuilder


class TestOverviewApp(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_title(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end',
                                       short_name="testassignment",
                                       parentnode__short_name="testperiod",  # Period
                                       parentnode__parentnode__short_name="testsubject"  # Subject
                                       )
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          'testsubject.testperiod.testassignment')

    def test_h1(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end',
                                       long_name="TESTASSIGNMENT",
                                       )
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEquals(mockresponse.selector.one('h1').alltext_normalized, 'TESTASSIGNMENT')

    def test_assignment_meta_has_two_students(self):
        assignment = mommy.make('core.Assignment')
        mommy.make('core.AssignmentGroup', parentnode=assignment, _quantity=2)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertTrue(
                mockresponse.selector.one('#devilry_admin_assignment_meta p').alltext_normalized.startswith(
                        '2 students'))

    def test_assignment_meta_has_no_students(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertTrue(
                mockresponse.selector.one('#devilry_admin_assignment_meta p').alltext_normalized.startswith(
                        '0 students'))

    def test_assignment_meta_one_examiner_configured(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        examiner1 = mommy.make('core.Examiner')
        assignment_group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        assignment_group.examiners.add(examiner1)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertTrue(
                mockresponse.selector.one('.devilry-admin-assignment-examiners-exists').alltext_normalized.startswith(
                        '1 examiner'))

    def test_assignment_meta_no_examiner_configured(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertFalse(
                mockresponse.selector.exists('.devilry-admin-assignment-examiners-exists'))

    def test_published_row(self):
        assignment = mommy.make('core.Assignment', publishing_time=datetime(2000, 1, 1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one('#devilry_admin_assignment_overview_published h3').alltext_normalized,
                "Was published: Jan 1 2000, 00:00")

    def test_published_row_published_time_in_future(self):
        assignment = mommy.make('core.Assignment', publishing_time=datetime(3000, 1, 1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one('#devilry_admin_assignment_overview_published h3').alltext_normalized,
                "Will be published: Jan 1 3000, 00:00")

    def test_published_row_buttons(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        "#devilry_admin_assignment_published_buttonrow a:nth-child(1)").alltext_normalized,
                'Publish now'
        )
        self.assertEqual(
                mockresponse.selector.one(
                        "#devilry_admin_assignment_published_buttonrow a:nth-child(2)").alltext_normalized,
                'Edit publishing time'
        )

    def test_settings_row(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one('#devilry_admin_assignment_overview_settings h2').alltext_normalized,
                "Settings")

    def test_settings_row_first_deadline(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_settings_first_deadline a').alltext_normalized,
                "Edit first deadline")

    def test_settings_row_first_deadline_description(self):
        assignment = mommy.make('core.Assignment', first_deadline=datetime(2000, 1, 1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_settings_first_deadline p').alltext_normalized,
                "The first deadline is Saturday January 1, 2000, 00:00. This deadline is common for all "
                "students unless a new deadline have been provided to a group.")

    def test_settings_row_anonymization(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_settings_anonymization a').alltext_normalized,
                "Anonymization")

    def test_settings_row_anonymization_description_when_anonymizationmode_off(self):
        assignment = mommy.make('core.Assignment')
        # default = ANONYMIZATIONMODE_OFF
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_settings_anonymization p').alltext_normalized,
                Assignment.ANONYMIZATIONMODE_CHOICES_DICT.get(Assignment.ANONYMIZATIONMODE_OFF))

    def test_settings_row_anonymization_description_when_anonymizationmode_semi_anonymous(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_settings_anonymization p').alltext_normalized,
                Assignment.ANONYMIZATIONMODE_CHOICES_DICT.get(Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        )

    def test_settings_row_anonymization_description_when_anonymizationmode_fully_anonymous(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_settings_anonymization p').alltext_normalized,
                Assignment.ANONYMIZATIONMODE_CHOICES_DICT.get(Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        )

    def test_gradingconfiguration_row_heading(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_gradingconfiguration h2').alltext_normalized,
                "Grading configuration")

    def test_gradingconfiguration_row_description(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_gradingconfiguration p').alltext_normalized,
                "How do you grade your students?")

    def test_gradingconfiguration_row_information_table_caption(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information table caption').alltext_normalized,
                "Current setup")

    def test_gradingconfiguration_row_information_table_head(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information table thead').alltext_normalized,
                "Description Grading")

    def test_gradingconfiguration_row_information_table_body(self):
        """

        TODO: need to be updated for the new grading configuration

        """
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'table tbody tr:nth-child(1)').alltext_normalized,
                "Examiner choosesTODO")
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'table tbody tr:nth-child(2)').alltext_normalized,
                "Students seeTODO")
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'table tbody tr:nth-child(3)').alltext_normalized,
                "Maximum number of points achievableTODO")
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'table tbody tr:nth-child(4)').alltext_normalized,
                "Minimum number of points required to passTODO")

    def test_utilities_row(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one('#devilry_admin_assignment_overview_utilities h2').alltext_normalized,
                "Utilities")

    def test_utilities_row_passed_previous(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_utilities_passed_previous a').alltext_normalized,
                "Passed previous semester")

    def test_utilities_row_passed_previous_description(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_utilities_passed_previous p').alltext_normalized,
                "Mark students that have passed this assignment previously.")

    def test_utilities_row_detektor(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_utilities_detektor a').alltext_normalized,
                "Detektor")

    def test_utilities_row_detektor_description(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_utilities_detektor p').alltext_normalized,
                'Compare programming code delivered by your students and '
                'get statistics about similarities in the uploaded files.')
