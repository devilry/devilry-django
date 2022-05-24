import unittest
from datetime import timedelta

import mock
from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone
from cradmin_legacy import cradmin_testhelpers
from cradmin_legacy.crinstance import reverse_cradmin_url
from model_bakery import baker

from devilry.apps.core import devilry_core_baker_factories as core_baker
from devilry.apps.core.models import Assignment
from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_admin.views.assignment import overview
from devilry.utils.datetimeutils import default_timezone_datetime


class TestOverviewApp(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_title(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end',
                                       short_name="testassignment",
                                       parentnode__short_name="testperiod",  # Period
                                       parentnode__parentnode__short_name="testsubject"  # Subject
                                       )
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'testsubject.testperiod.testassignment')

    def test_devilry_admin_assignment_edit_long_name(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(mockresponse.selector.one('#devilry_admin_assignment_edit_long_name').alltext_normalized,
                         'Edit name')

    def test_h1(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end', long_name="TESTASSIGNMENT")
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized, 'TESTASSIGNMENT')

    # Todo: Remove
    # def test_publish_now_info_box(self):
    #     assignment = baker.make('core.Assignment', publishing_time=timezone.now() + timedelta(days=1))
    #     group = baker.make('core.AssignmentGroup', parentnode=assignment)
    #     core_baker.candidate(group=group)
    #     core_baker.examiner(group=group)
    #     baker.make('core.RelatedStudent', period=assignment.period)
    #     baker.make('core.RelatedExaminer', period=assignment.period)
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
    #     self.assertIn(
    #         'Ready to publish the assignment',
    #         mockresponse.selector.one('#devilry_admin_assignment_overview_info_box').alltext_normalized
    #     )
    #     self.assertEqual(
    #         mock.call(appname='overview', args=(assignment.id, ), kwargs={}, viewname='publish_assignment_now'),
    #         mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
    #     )
    #     self.assertTrue(mockresponse.selector.exists('#devilry_admin_assignment_published_publishnow_form_info_box'))

    def test_published_row(self):
        assignment = baker.make('core.Assignment', publishing_time=default_timezone_datetime(2000, 1, 1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one('#devilry_admin_assignment_overview_published h3').alltext_normalized,
            "Was published: Jan 1 2000, 00:00")

    def test_published_row_published_time_in_future(self):
        assignment = baker.make('core.Assignment', publishing_time=default_timezone_datetime(3000, 1, 1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one('#devilry_admin_assignment_overview_published h3').alltext_normalized,
            "Will be published: Jan 1 3000, 00:00")

    def test_published_row_buttons(self):
        assignment = baker.make('core.Assignment', publishing_time=default_timezone_datetime(3000, 1, 1))
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
        assignment = baker.make('core.Assignment', publishing_time=default_timezone_datetime(2000, 1, 1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertFalse(
            mockresponse.selector.exists(
                "#devilry_admin_assignment_published_publishnow_form")
        )

    def test_settings_row_first_deadline(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_first_deadline a').alltext_normalized,
            "Edit first deadline")

    def test_settings_row_first_deadline_description(self):
        assignment = baker.make('core.Assignment', first_deadline=default_timezone_datetime(2000, 1, 1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_first_deadline p').alltext_normalized,
            "The first deadline is Saturday January 1, 2000, 00:00. This deadline is common for all "
            "students unless a new deadline have been provided to a group.")

    def test_settings_row_anonymization(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_anonymization a').alltext_normalized,
            "Edit anonymization mode")

    def test_settings_row_anonymization_description_when_anonymizationmode_off(self):
        assignment = baker.make('core.Assignment')
        # default = ANONYMIZATIONMODE_OFF
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_anonymization p').alltext_normalized,
            Assignment.ANONYMIZATIONMODE_CHOICES_DICT.get(Assignment.ANONYMIZATIONMODE_OFF))

    def test_settings_row_anonymization_description_when_anonymizationmode_semi_anonymous(self):
        assignment = baker.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_anonymization p').alltext_normalized,
            Assignment.ANONYMIZATIONMODE_CHOICES_DICT.get(Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        )

    def test_settings_row_anonymization_description_when_anonymizationmode_fully_anonymous(self):
        assignment = baker.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_anonymization p').alltext_normalized,
            Assignment.ANONYMIZATIONMODE_CHOICES_DICT.get(Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        )

    def test_gradingconfiguration_row_heading(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_gradingconfiguration h2').alltext_normalized,
            "Grading configuration")

    # def test_gradingconfiguration_row_information_table_caption(self):
    #     assignment = baker.make('core.Assignment')
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
    #     self.assertEqual(
    #             mockresponse.selector.one(
    #                     '#devilry_admin_assignment_overview_gradingconfiguration_information table caption').alltext_normalized,
    #             "Current setup")

    # def test_gradingconfiguration_row_information_table_head(self):
    #     assignment = baker.make('core.Assignment')
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
    #     self.assertEqual(
    #             mockresponse.selector.one(
    #                     '#devilry_admin_assignment_overview_gradingconfiguration_information table thead').alltext_normalized,
    #             "Description Grading")

    def test_gradingconfiguration_examiner_chooses(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dt:nth-child(1)').alltext_normalized,
            'Examiner chooses')

    def test_gradingconfiguration_examiner_chooses_passed_failed(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dd:nth-child(2)').alltext_normalized,
            str(Assignment.GRADING_SYSTEM_PLUGIN_ID_CHOICES_DICT.get(
                Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)))

    def test_gradingconfiguration_examiner_chooses_points(self):
        assignment = baker.make('core.Assignment', grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dd:nth-child(2)').alltext_normalized,
            str(Assignment.GRADING_SYSTEM_PLUGIN_ID_CHOICES_DICT.get(
                Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)))

    # def test_gradingconfiguration_examiner_chooses_schema(self):
    #     assignment = baker.make('core.Assignment', grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_SCHEMA)
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
    #     self.assertEqual(
    #             mockresponse.selector.one(
    #                     '#devilry_admin_assignment_overview_gradingconfiguration_information '
    #                     'table tbody tr:nth-child(1) td:nth-child(2)').alltext_normalized,
    #             str(Assignment.GRADING_SYSTEM_PLUGIN_ID_CHOICES_DICT.get(
    #                     Assignment.GRADING_SYSTEM_PLUGIN_ID_SCHEMA)))

    def test_gradingconfiguration_students_see(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dt:nth-child(3)').alltext_normalized,
            "Students see")

    def test_gradingconfiguration_students_see_passed_failed(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dd:nth-child(4)').alltext_normalized,
            str(Assignment.POINTS_TO_GRADE_MAPPER_CHOICES_DICT.get(
                Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)))

    def test_gradingconfiguration_students_see_points(self):
        assignment = baker.make('core.Assignment', points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dd:nth-child(4)').alltext_normalized,
            str(Assignment.POINTS_TO_GRADE_MAPPER_CHOICES_DICT.get(
                Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)))

    def test_gradingconfiguration_students_see_schema(self):
        assignment = baker.make('core.Assignment',
                                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE)
        point_to_grade_map = baker.make('core.PointToGradeMap', assignment=assignment)
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=5,
                   maximum_points=9, grade='F')
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=10,
                   maximum_points=14,grade='E')
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=15,
                   maximum_points=19, grade='D')
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=20,
                   maximum_points=24, grade='C')
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=25,
                   maximum_points=29, grade='B')
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=30,
                   maximum_points=35, grade='A')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dd:nth-child(4)').alltext_normalized,
            'F, E, D, C, B or A')

    def test_gradingconfiguration_max_points(self):
        assignment = baker.make('core.Assignment', grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dt:nth-child(5)').alltext_normalized,
            "Maximum number of points achievable")

    def test_gradingconfiguration_max_points_100(self):
        assignment = baker.make('core.Assignment', max_points=100,
                                grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dd:nth-child(6)').alltext_normalized,
            "100")

    def test_gradingconfiguration_min_points(self):
        assignment = baker.make('core.Assignment', grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dt:nth-child(7)').alltext_normalized,
            "Minimum number of points required to pass")

    def test_gradingconfiguration_min_points_0(self):
        assignment = baker.make('core.Assignment', passing_grade_min_points=0,
                                grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_gradingconfiguration_information '
                'dl:nth-child(1) dd:nth-child(8)').alltext_normalized,
            "0")

    def test_utilities_row_passed_previous(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_utilities_passed_previous h3').alltext_normalized,
            "Passed previous semester")

    def test_utilities_row_passed_previous_description(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_utilities_passed_previous p').alltext_normalized,
            "Mark students that have passed this assignment previously.")

    def test_utilities_button_passed_previous_period_text(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_utilities_passed_previous_buttons'
            ).alltext_normalized,
            'Edit passed previous semester'
        )

    def test_settings_project_groups_sanity(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_projectgroups h3'
            ).alltext_normalized,
            'Project groups'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_projectgroups p'
            ).alltext_normalized,
            'Students can not create project groups on their own. As an administrator you are '
            'able to create the groups in the "Students" overview.'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_projectgroups_buttons a'
            ).alltext_normalized,
            'Edit project group settings'
        )
    
    def test_settings_project_groups_turned_on(self):
        assignment = baker.make('core.Assignment', students_can_create_groups=True)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_projectgroups h3'
            ).alltext_normalized,
            'Project groups'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_projectgroups p'
            ).alltext_normalized,
            'Student can create project groups on their own.'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_projectgroups_buttons a'
            ).alltext_normalized,
            'Edit project group settings'
        )

    def test_settings_anonymization_sanity(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_anonymization h3'
            ).alltext_normalized,
            'Anonymization'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_anonymization p'
            ).alltext_normalized,
            'OFF. Normal assignment where semester and course admins can see everything, '
            'and examiners and students can see each others names and contact information.'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_anonymization_buttons a'
            ).alltext_normalized,
            'Edit anonymization mode'
        )
    
    def test_settings_anonymization_semi_anonymous(self):
        assignment = baker.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_anonymization h3'
            ).alltext_normalized,
            'Anonymization'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_anonymization p'
            ).alltext_normalized,
            'SEMI ANONYMOUS. Students and examiners can not see information about each other. '
            'Comments added by course admins are not anonymized. '
            'Semester admins do not have access to the assignment in the admin UI. Course admins '
            'have the same permissions as for "OFF".'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_anonymization_buttons a'
            ).alltext_normalized,
            'Edit anonymization mode'
        )

    def test_settings_anonymization_fully_anonymous(self):
        assignment = baker.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_anonymization h3'
            ).alltext_normalized,
            'Anonymization'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_anonymization p'
            ).alltext_normalized,
            'FULLY ANONYMIZED. Intended for exams where course admins are examiners. '
            'Students and examiners can not see information about each other. Hidden '
            'from semester admins. Course admins can not view grading details. Only '
            'departmentadmins and superusers can change this back to another "anoymization mode" '
            'when feedback has been added to the assignment. Course admins can not edit '
            'examiners after the first feedback is provided.'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_anonymization_buttons a'
            ).alltext_normalized,
            'Edit anonymization mode'
        )
    
    @override_settings(DEFAULT_DEADLINE_HANDLING_METHOD=0)
    def test_settings_deadline_handling_no_access_sanity(self):
        assignment = baker.make('core.Assignment')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, requestuser=testuser)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_deadline_handling h3'
            ).alltext_normalized,
            'Deadline handling'
        )
        self.assertEqual(
            mockresponse.selector.list(
                '#devilry_admin_assignment_overview_settings_deadline_handling p'
            )[0].alltext_normalized,
            'SOFT. Students can add deliveries and comment after the deadline has expired.'
        )
        self.assertEqual(
            mockresponse.selector.list(
                '#devilry_admin_assignment_overview_settings_deadline_handling p'
            )[1].alltext_normalized,
            'You do not have access to change this setting.'
        )

    @override_settings(DEFAULT_DEADLINE_HANDLING_METHOD=0)
    def test_settings_deadline_handling_periodadmin_no_access_sanity(self):
        assignment = baker.make('core.Assignment')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=baker.make('devilry_account.PeriodPermissionGroup',
                                              period=assignment.parentnode).permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, requestuser=testuser)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_deadline_handling h3'
            ).alltext_normalized,
            'Deadline handling'
        )
        self.assertEqual(
            mockresponse.selector.list(
                '#devilry_admin_assignment_overview_settings_deadline_handling p'
            )[0].alltext_normalized,
            'SOFT. Students can add deliveries and comment after the deadline has expired.'
        )
        self.assertEqual(
            mockresponse.selector.list(
                '#devilry_admin_assignment_overview_settings_deadline_handling p'
            )[1].alltext_normalized,
            'You do not have access to change this setting.'
        )

    @override_settings(DEFAULT_DEADLINE_HANDLING_METHOD=0)
    def test_settings_deadline_handling_soft_subjectadmin_has_access_sanity(self):
        assignment = baker.make('core.Assignment')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=baker.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
                                              subject=assignment.parentnode.parentnode).permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, requestuser=testuser)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_deadline_handling h3'
            ).alltext_normalized,
            'Deadline handling'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_deadline_handling p'
            ).alltext_normalized,
            'SOFT. Students can add deliveries and comment after the deadline has expired.'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_deadline_handling_buttons a'
            ).alltext_normalized,
            'Edit deadline handling'
        )
    
    @override_settings(DEFAULT_DEADLINE_HANDLING_METHOD=0)
    def test_settings_deadline_handling_hard_subjectadmin_has_access_sanity(self):
        assignment = baker.make('core.Assignment', deadline_handling=1)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=baker.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
                                              subject=assignment.parentnode.parentnode).permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, requestuser=testuser)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_deadline_handling h3'
            ).alltext_normalized,
            'Deadline handling'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_deadline_handling p'
            ).alltext_normalized,
            'HARD. Students can not add deliveries or comment after the deadline has expired.'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_deadline_handling_buttons a'
            ).alltext_normalized,
            'Edit deadline handling'
        )

    def test_settings_examiner_selfassign_sanity(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_selfassign h3'
            ).alltext_normalized,
            'Examiner self-assign'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_selfassign p'
            ).alltext_normalized,
            'Examiners can not assign themselves to project groups on this assignment.'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_selfassign_buttons a'
            ).alltext_normalized,
            'Edit self-assign settings'
        )
    
    def test_settings_examiner_selfassign_turned_on(self):
        assignment = baker.make('core.Assignment', examiners_can_self_assign=True, examiner_self_assign_limit=2)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_selfassign h3'
            ).alltext_normalized,
            'Examiner self-assign'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_selfassign p'
            ).alltext_normalized,
            'Examiners can assign themselves to project groups on this assignment. '
            'Examiner self-assign limit for each project group is set to 2.'
        )
        self.assertEqual(
            mockresponse.selector.one(
                '#devilry_admin_assignment_overview_settings_selfassign_buttons a'
            ).alltext_normalized,
            'Edit self-assign settings'
        )


class TestOverviewExaminerSection(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_sanity_no_relatedexaminer_no_other_warnings_shown(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Warnings rendered
        self.assertTrue(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_empty_semester_warning'))

        # Warnings not rendered
        self.assertFalse(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_students_without_examiner_warning'))
        self.assertFalse(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_no_examiners_on_assignment'))
        self.assertFalse(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_on_semester_not_on_assignment'))

    def test_sanity_students_without_examiners_and_no_examiners(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        baker.make('core.RelatedExaminer', period=assignment.parentnode)
        baker.make('core.Candidate', assignment_group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Warnings rendered
        self.assertTrue(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_students_without_examiner_warning'))
        self.assertTrue(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_no_examiners_on_assignment'))

        # Warnings not rendered
        self.assertFalse(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_empty_semester_warning'))
        self.assertFalse(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_on_semester_not_on_assignment'))

    def test_sanity_students_without_examiners_and_more_relatedexaminer_than_examiners(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        baker.make('core.RelatedExaminer', period=assignment.parentnode)
        related_examiner = baker.make('core.RelatedExaminer', period=assignment.parentnode)
        baker.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup__parentnode=assignment)
        baker.make('core.Candidate', assignment_group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Warnings rendered
        self.assertTrue(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_students_without_examiner_warning'))
        self.assertTrue(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_on_semester_not_on_assignment'))

        # Warnings not rendered
        self.assertFalse(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_empty_semester_warning'))
        self.assertFalse(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_examiner_no_examiners_on_assignment'))

    def test_assignment_meta_one_distinct_examiner_configured(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        relatedexaminer = baker.make('core.RelatedExaminer', period=assignment.period)
        baker.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup__parentnode=assignment)
        baker.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one('.devilry-admin-assignment-examiners-exists').alltext_normalized,
            '1 examiner(s) configured')

    def test_assignment_meta_multiple_examiners_configured(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        baker.make('core.Examiner', assignmentgroup__parentnode=assignment)
        baker.make('core.Examiner', assignmentgroup__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one('#id_devilry_admin_assignment_examiners_meta_count_text').alltext_normalized,
            '2 examiner(s) configured')

    def test_assignment_meta_no_examiner_configured(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one('.devilry-admin-assignment-examiners-does-not-exist').alltext_normalized,
            'No examiners configured')

    def test_no_examiners_on_semester_warning(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Check warning exists
        self.assertTrue(
            mockresponse.selector.exists('#id_devilry_admin_assignment_examiner_empty_semester_warning'))

        # Check warning text
        self.assertTrue(mockresponse.selector.one('#id_devilry_admin_assignment_examiner_empty_semester_warning')
                        .alltext_normalized,
                        'warning: Go to the semester page and add/activate examiners')

        # Check warning link
        url = reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='overview',
            roleid=assignment.parentnode.id,
            viewname='INDEX'
        )
        self.assertEqual(
            url,
            mockresponse.selector.one(
                '#id_devilry_admin_assignment_examiner_empty_semester_warning > strong > a').get('href'))

    def test_students_without_examiners_exists_warning(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        baker.make('core.RelatedExaminer', period=assignment.period)
        baker.make('core.Candidate', assignment_group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Check warning exists
        self.assertTrue(
            mockresponse.selector.exists('#id_devilry_admin_assignment_examiner_students_without_examiner_warning'))

        # Check warning text
        self.assertIn(
            'warning: There are students with no examiners assigned to them',
            mockresponse.selector.one('#id_devilry_admin_assignment_examiner_students_without_examiner_warning')
                .alltext_normalized)

        # Check warning link
        url = reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='examineroverview',
            roleid=assignment.id,
            viewname='INDEX'
        )
        self.assertEqual(
            url,
            mockresponse.selector.one(
                '#id_devilry_admin_assignment_examiner_students_without_examiner_warning > strong > a').get('href'))

    def test_no_examiners_configured_for_assignment_groups_warning(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        baker.make('core.RelatedExaminer', period=assignment.period)
        baker.make('core.Candidate', assignment_group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Check warning exists
        self.assertTrue(
            mockresponse.selector.exists('#id_devilry_admin_assignment_examiner_no_examiners_on_assignment'))

        # Check warning texts
        self.assertIn(
            'warning: No examiners configured',
            mockresponse.selector.one('#id_devilry_admin_assignment_examiner_no_examiners_on_assignment')
                .alltext_normalized)
        self.assertIn(
            'Only configured examiners can see and correct deliveries from students.',
            mockresponse.selector.one('#id_devilry_admin_assignment_examiner_no_examiners_on_assignment')
                .alltext_normalized)

        # Check warning links
        url = reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='examineroverview',
            viewname='INDEX',
            roleid=assignment.id)
        self.assertEqual(
            url,
            mockresponse.selector.one(
                '#id_devilry_admin_assignment_examiner_no_examiners_on_assignment > strong > a').get('href'))

    def test_fewer_examiners_than_relatedexaminers_on_semester_note(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        baker.make('core.RelatedExaminer', period=assignment.period)
        related_examiner = baker.make('core.RelatedExaminer', period=assignment.period)
        baker.make('core.Examiner', relatedexaminer=related_examiner, assignmentgroup__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Check warning exists
        self.assertTrue(
            mockresponse.selector.exists('#id_devilry_admin_assignment_examiner_on_semester_not_on_assignment'))

        # Check warning text
        self.assertIn(
            'note: There are examiners on the semester that are not assigned to any students',
            mockresponse.selector.one('#id_devilry_admin_assignment_examiner_on_semester_not_on_assignment')
                .alltext_normalized)

        # Check warning link
        url = reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='examineroverview',
            viewname='INDEX',
            roleid=assignment.id)
        self.assertEqual(
            url,
            mockresponse.selector.one(
                '#id_devilry_admin_assignment_examiner_on_semester_not_on_assignment > a').get('href'))


class TestOverviewStudentSection(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_sanity_no_relatedstudents_no_other_warnings_shown(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Warnings rendered
        self.assertTrue(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_student_no_active_students_on_semester'))

        # Warnings not rendered
        self.assertFalse(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_student_no_students_on_assignment'))
        self.assertFalse(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_student_on_semester_not_on_assignment'))

    def test_sanity_no_candidates_on_assignment(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        baker.make('core.RelatedStudent', period=assignment.parentnode)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Warnings rendered
        self.assertTrue(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_student_no_students_on_assignment'))

        # Warnings not rendered
        self.assertFalse(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_student_no_active_students_on_semester'))
        self.assertFalse(mockresponse.selector.exists(
            '#id_devilry_admin_assignment_student_on_semester_not_on_assignment'))

    def test_meta_text_has_two_candidates_and_two_assignment_groups(self):
        assignment = baker.make('core.Assignment')
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Candidate', assignment_group=group1)
        baker.make('core.Candidate', assignment_group=group2)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one('#id_devilry_admin_assignment_students_meta_count_text').alltext_normalized,
            '2 students organized in 2 project groups')

    def test_meta_text_has_no_students(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertEqual(
            mockresponse.selector.one('#id_devilry_admin_assignment_students_meta_count_text').alltext_normalized,
            'No students on the assignment')

    def test_meta_text_has_multiple_students_in_group(self):
        assignment = baker.make('core.Assignment')
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Candidate', assignment_group=group1)
        baker.make('core.Candidate', assignment_group=group2)
        baker.make('core.Candidate', assignment_group=group2)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)
        self.assertTrue(
            mockresponse.selector.one('#id_devilry_admin_assignment_students_meta_count_text').alltext_normalized,
            '3 students organized in 2 project groups')

    def test_no_related_students_on_semester(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Check warning exists
        self.assertTrue(
            mockresponse.selector.exists('#id_devilry_admin_assignment_student_no_active_students_on_semester'))

        # Check warning text
        self.assertIn(
            'warning: Go to the semester page and add/activate students',
            mockresponse.selector.one('#id_devilry_admin_assignment_student_no_active_students_on_semester')
                .alltext_normalized)

        # Check warning link
        url = reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='overview',
            viewname='INDEX',
            roleid=assignment.parentnode.id)
        self.assertEqual(
            url,
            mockresponse.selector.one(
                '#id_devilry_admin_assignment_student_no_active_students_on_semester > strong > a').get('href'))

    def test_no_candidates_warning(self):
        assignment = baker.make('core.Assignment')
        baker.make('core.RelatedStudent', period=assignment.parentnode)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Check warning exists
        self.assertTrue(mockresponse.selector.exists('#id_devilry_admin_assignment_student_no_students_on_assignment'))

        # Check warning texts
        self.assertIn(
            'warning: No students added to the assignment',
            mockresponse.selector.one('#id_devilry_admin_assignment_student_no_students_on_assignment')
                .alltext_normalized)
        self.assertIn(
            'Only students added to an assignment can see the assignment and add deliveries',
            mockresponse.selector.one('#id_devilry_admin_assignment_student_no_students_on_assignment')
                .alltext_normalized)

        # Check warning link
        url = reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='create_groups',
            viewname='INDEX',
            roleid=assignment.id)
        self.assertEqual(
            url,
            mockresponse.selector.one(
                '#id_devilry_admin_assignment_student_no_students_on_assignment > strong > a').get('href'))

    def test_students_on_the_semester_that_are_not_on_the_assignment_warning(self):
        assignment = baker.make('core.Assignment')
        baker.make('core.RelatedStudent', period=assignment.parentnode)
        related_student = baker.make('core.RelatedStudent', period=assignment.parentnode)
        baker.make('core.Candidate', relatedstudent=related_student, assignment_group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment)

        # Check warning exists
        self.assertTrue(mockresponse.selector.exists('#id_devilry_admin_assignment_student_on_semester_not_on_assignment'))

        # Check warning text
        self.assertIn(
            'note: There are students who are on the semester, but not on the assignment',
            mockresponse.selector.one('#id_devilry_admin_assignment_student_on_semester_not_on_assignment')
                .alltext_normalized)

        # Check warning link
        url = reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='create_groups',
            viewname='INDEX',
            roleid=assignment.id)
        self.assertEqual(
            url,
            mockresponse.selector.one(
                '#id_devilry_admin_assignment_student_on_semester_not_on_assignment > a').get('href'))
