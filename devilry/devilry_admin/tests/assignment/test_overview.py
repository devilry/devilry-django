from datetime import datetime, timedelta

import mock
from django.conf import settings
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment import overview
from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from django_cradmin.crinstance import reverse_cradmin_url


class TestOverviewApp(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_title(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end',
                                       short_name="testassignment",
                                       parentnode__short_name="testperiod",  # Period
                                       parentnode__parentnode__short_name="testsubject"  # Subject
                                       )
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'testsubject.testperiod.testassignment')

    def test_devilry_admin_assignment_edit_long_name(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(mockresponse.selector.one('#devilry_admin_assignment_edit_long_name').alltext_normalized,
                         'Edit name')

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
        # testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        relatedexaminer = mommy.make('core.RelatedExaminer', period=assignment.period)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup__parentnode=assignment)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup__parentnode=assignment)
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
        assignment = mommy.make('core.Assignment', publishing_time=datetime(3000, 1, 1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_published_publishnow_form input[type="submit"]')['value'],
                'Publish now'
        )
        self.assertEqual(
                mockresponse.selector.one(
                        "#devilry_admin_assignment_published_buttonrow a").alltext_normalized,
                'Edit publishing time'
        )

    def test_published_row_buttons_when_already_published(self):
        assignment = mommy.make('core.Assignment', publishing_time=datetime(2000, 1, 1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertFalse(
                mockresponse.selector.exists(
                        "#devilry_admin_assignment_published_publishnow_form")
        )

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
                "Edit anonymization mode")

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

    # def test_gradingconfiguration_row_information_table_caption(self):
    #     assignment = mommy.make('core.Assignment')
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
    #     self.assertEqual(
    #             mockresponse.selector.one(
    #                     '#devilry_admin_assignment_overview_gradingconfiguration_information table caption').alltext_normalized,
    #             "Current setup")

    # def test_gradingconfiguration_row_information_table_head(self):
    #     assignment = mommy.make('core.Assignment')
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
    #     self.assertEqual(
    #             mockresponse.selector.one(
    #                     '#devilry_admin_assignment_overview_gradingconfiguration_information table thead').alltext_normalized,
    #             "Description Grading")

    def test_gradingconfiguration_examiner_chooses(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEquals(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dt:nth-child(1)').alltext_normalized,
            'Examiner chooses')

    def test_gradingconfiguration_examiner_chooses_passed_failed(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'dl:nth-child(1) dd:nth-child(2)').alltext_normalized,
                str(Assignment.GRADING_SYSTEM_PLUGIN_ID_CHOICES_DICT.get(
                        Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)))

    def test_gradingconfiguration_examiner_chooses_points(self):
        assignment = mommy.make('core.Assignment', grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'dl:nth-child(1) dd:nth-child(2)').alltext_normalized,
                str(Assignment.GRADING_SYSTEM_PLUGIN_ID_CHOICES_DICT.get(
                        Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)))

    # def test_gradingconfiguration_examiner_chooses_schema(self):
    #     assignment = mommy.make('core.Assignment', grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_SCHEMA)
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
    #     self.assertEqual(
    #             mockresponse.selector.one(
    #                     '#devilry_admin_assignment_overview_gradingconfiguration_information '
    #                     'table tbody tr:nth-child(1) td:nth-child(2)').alltext_normalized,
    #             str(Assignment.GRADING_SYSTEM_PLUGIN_ID_CHOICES_DICT.get(
    #                     Assignment.GRADING_SYSTEM_PLUGIN_ID_SCHEMA)))

    def test_gradingconfiguration_students_see(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'dl:nth-child(1) dt:nth-child(3)').alltext_normalized,
                "Students see")

    def test_gradingconfiguration_students_see_passed_failed(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'dl:nth-child(1) dd:nth-child(4)').alltext_normalized,
                str(Assignment.POINTS_TO_GRADE_MAPPER_CHOICES_DICT.get(
                        Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)))

    def test_gradingconfiguration_students_see_points(self):
        assignment = mommy.make('core.Assignment', points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'dl:nth-child(1) dd:nth-child(4)').alltext_normalized,
                str(Assignment.POINTS_TO_GRADE_MAPPER_CHOICES_DICT.get(
                        Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)))

    def test_gradingconfiguration_students_see_schema(self):
        assignment = mommy.make('core.Assignment',
                                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE)
        point_to_grade_map = mommy.make('core.PointToGradeMap', assignment=assignment)
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=5,
                   maximum_points=9, grade='F')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=10,
                   maximum_points=14,grade='E')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=15,
                   maximum_points=19, grade='D')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=20,
                   maximum_points=24, grade='C')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=25,
                   maximum_points=29, grade='B')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=30,
                   maximum_points=35, grade='A')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'dl:nth-child(1) dd:nth-child(4)').alltext_normalized,
                'F, E, D, C, B or A')

    def test_gradingconfiguration_max_points(self):
        assignment = mommy.make('core.Assignment', grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'dl:nth-child(1) dt:nth-child(5)').alltext_normalized,
                "Maximum number of points achievable")

    def test_gradingconfiguration_max_points_100(self):
        assignment = mommy.make('core.Assignment', max_points=100,
                                grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'dl:nth-child(1) dd:nth-child(6)').alltext_normalized,
                "100")

    def test_gradingconfiguration_min_points(self):
        assignment = mommy.make('core.Assignment', grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'dl:nth-child(1) dt:nth-child(7)').alltext_normalized,
                "Minimum number of points required to pass")

    def test_gradingconfiguration_min_points_0(self):
        assignment = mommy.make('core.Assignment', passing_grade_min_points=0,
                                grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_gradingconfiguration_information '
                        'dl:nth-child(1) dd:nth-child(8)').alltext_normalized,
                "0")

    def test_utilities_row_passed_previous(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_utilities_passed_previous h3').alltext_normalized,
                "Passed previous semester")

    def test_utilities_row_passed_previous_description(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
                mockresponse.selector.one(
                        '#devilry_admin_assignment_overview_utilities_passed_previous p').alltext_normalized,
                "Mark students that have passed this assignment previously.")

    # def test_utilities_row_detektor(self):
    #     assignment = mommy.make('core.Assignment')
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
    #     self.assertEqual(
    #             mockresponse.selector.one(
    #                     '#devilry_admin_assignment_overview_utilities_detektor a').alltext_normalized,
    #             "Detektor")
    #
    # def test_utilities_row_detektor_description(self):
    #     assignment = mommy.make('core.Assignment')
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
    #     self.assertEqual(
    #             mockresponse.selector.one(
    #                     '#devilry_admin_assignment_overview_utilities_detektor p').alltext_normalized,
    #             'Compare programming code delivered by your students and '
    #             'get statistics about similarities in the uploaded files.')


class TestOverviewInfoBox(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_no_students_on_period(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertIn(
            'There are no students on the semester',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box').alltext_normalized
        )
        self.assertIn(
            'Add students',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box > p > a').alltext_normalized
        )
        url = reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='students',
            roleid=assignment.period.id,
            viewname='add')
        self.assertEqual(
            url,
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box > p > a').get('href')
        )

    def test_no_students_on_the_assignment(self):
        assignment = mommy.make('core.Assignment')
        mommy.make('core.RelatedStudent', period=assignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertIn(
            'There are no students on the assignment',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box').alltext_normalized
        )
        self.assertIn(
            'Add students',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box > p > a').alltext_normalized
        )
        self.assertEqual(
            mock.call(appname='create_groups', args=(), kwargs={}, viewname='manual-select'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )

    def test_no_examiners_on_period(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('core.RelatedStudent', period=assignment.period)
        core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertIn(
            'There are no examiners on the semester',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box').alltext_normalized
        )
        self.assertIn(
            'Add examiners',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box > p > a').alltext_normalized
        )
        url = reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='examiners',
            roleid=assignment.period.id,
            viewname='add')
        self.assertEqual(
            url,
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box > p > a').get('href')
        )

    def test_no_examiners_on_the_assignment(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('core.RelatedStudent', period=assignment.period)
        mommy.make('core.RelatedExaminer', period=assignment.period)
        core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertIn(
            'There are no examiners on the assignment',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box').alltext_normalized
        )
        self.assertIn(
            'Add examiners',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box > p > a').alltext_normalized
        )
        self.assertEqual(
            mock.call(appname='examineroverview', args=(), kwargs={}, viewname='INDEX'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )

    def test_publish_now(self):
        assignment = mommy.make('core.Assignment', publishing_time=datetime.now() + timedelta(days=1))
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        core_mommy.candidate(group=group)
        core_mommy.examiner(group=group)
        mommy.make('core.RelatedStudent', period=assignment.period)
        mommy.make('core.RelatedExaminer', period=assignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertIn(
            'Everything looks good, ready to publish',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box').alltext_normalized
        )
        self.assertEqual(
            mock.call(appname='overview', args=(assignment.id, ), kwargs={}, viewname='publish_assignment_now'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )
        self.assertTrue(mockresponse.selector.exists('#devilry_admin_assignment_published_publishnow_form_info_box'))

    def test_still_students_who_are_on_the_semester_but_not_on_the_assignemnt(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        relatedstudent = mommy.make('core.RelatedStudent', period=assignment.period)
        mommy.make('core.Candidate', assignment_group=group, relatedstudent=relatedstudent)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=assignment.period)
        mommy.make('core.Examiner', assignmentgroup=group, relatedexaminer=relatedexaminer)
        mommy.make('core.RelatedStudent', period=assignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertIn(
            'There are still students who are on the semester, but not on the assignment',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box').alltext_normalized
        )
        self.assertIn(
            'Add students',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box > p > a').alltext_normalized
        )
        self.assertEqual(
            mock.call(appname='create_groups', args=(), kwargs={}, viewname='manual-select'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )

    def test_still_examiners_who_are_on_the_semester_but_not_on_the_assignment(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        relatedstudent = mommy.make('core.RelatedStudent', period=assignment.period)
        mommy.make('core.Candidate', assignment_group=group, relatedstudent=relatedstudent)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=assignment.period)
        mommy.make('core.Examiner', assignmentgroup=group, relatedexaminer=relatedexaminer)
        mommy.make('core.RelatedExaminer', period=assignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertIn(
            'There are still examiners who are on the semester, but not on the assignment',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box').alltext_normalized
        )
        self.assertIn(
            'Add examiners',
            mockresponse.selector.one('#devilry_admin_assignment_overview_info_box > p > a').alltext_normalized
        )
        self.assertEqual(
            mock.call(appname='examineroverview', args=(), kwargs={}, viewname='INDEX'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )

    def test_info_box_is_not_shown(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        core_mommy.candidate(group=group)
        core_mommy.examiner(group=group)
        mommy.make('core.RelatedStudent', period=assignment.period)
        mommy.make('core.RelatedExaminer', period=assignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertFalse(
            mockresponse.selector.exists('#devilry_admin_assignment_overview_info_box')
        )
