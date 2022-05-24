from django import test
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.utils.api import api_test_mixin
from devilry.devilry_statistics.api.assignment import examiner_average_grading_points
from devilry.devilry_group import devilry_group_baker_factories as group_baker


class TestExaminerAverageGradingPointsApi(test.TestCase, api_test_mixin.ApiTestMixin):
    apiview_class = examiner_average_grading_points.ExaminerAverageGradingPointsApi

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_not_authenticated(self):
        response = self.make_get_request()
        self.assertEqual(response.status_code, 403)

    def test_validator_assignment_id_missing_raises_403(self):
        # Raises 403 because permission query is executed first (requires assignment_id)
        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'relatedexaminer_id': 1})
        self.assertEqual(response.status_code, 403)

    def test_validator_relatedexaminer_id_missing(self):
        assignment = baker.make('core.Assignment')
        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id})
        self.assertEqual(str(response.data['relatedexaminer_id'][0]), 'This field is required.')
        self.assertEqual(response.status_code, 400)

    def test_user_has_no_access(self):
        assignment = baker.make('core.Assignment')
        relatedexaminer = baker.make('core.RelatedExaminer', user__fullname='Test User')
        response = self.make_get_request(
            requestuser=self.make_user(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.status_code, 403)

    def test_period_admin_on_different_period_does_not_have_access(self):
        other_period = baker.make('core.Period')
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        requestuser = self.make_user()
        permissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                     period=other_period)
        baker.make('devilry_account.PermissionGroupUser',
                   user=requestuser,
                   permissiongroup=permissiongroup.permissiongroup)
        response = self.make_get_request(
            requestuser=requestuser,
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': 1})
        self.assertEqual(response.status_code, 403)

    def test_period_admin_has_access(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
        requestuser = self.make_user()
        permissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                     period=period)
        baker.make('devilry_account.PermissionGroupUser',
                   user=requestuser,
                   permissiongroup=permissiongroup.permissiongroup)
        response = self.make_get_request(
            requestuser=requestuser,
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.status_code, 200)

    def test_subject_admin_on_different_subject_does_not_have_access(self):
        other_subject = baker.make('core.Subject')
        subject = baker.make('core.Subject')
        period = baker.make('core.Period', parentnode=subject)
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        requestuser = self.make_user()
        permissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                     subject=other_subject)
        baker.make('devilry_account.PermissionGroupUser',
                   user=requestuser,
                   permissiongroup=permissiongroup.permissiongroup)
        response = self.make_get_request(
            requestuser=requestuser,
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.status_code, 403)

    def test_subject_admin_has_access(self):
        subject = baker.make('core.Subject')
        period = baker.make('core.Period', parentnode=subject)
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
        requestuser = self.make_user()
        permissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                     permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                     subject=subject)
        baker.make('devilry_account.PermissionGroupUser',
                   user=requestuser,
                   permissiongroup=permissiongroup.permissiongroup)
        response = self.make_get_request(
            requestuser=requestuser,
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.status_code, 200)

    def test_department_admin_has_access(self):
        subject = baker.make('core.Subject')
        period = baker.make('core.Period', parentnode=subject)
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
        requestuser = self.make_user()
        permissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                     subject=subject, permissiongroup__grouptype='departmentadmin')
        baker.make('devilry_account.PermissionGroupUser',
                   user=requestuser,
                   permissiongroup=permissiongroup.permissiongroup)
        response = self.make_get_request(
            requestuser=requestuser,
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.status_code, 200)

    def __make_group_for_relatedexaminer(self, assignment, relatedexaminer, grading_points):
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=group)
        group_baker.feedbackset_first_attempt_published(group=group, grading_points=grading_points)
        return group

    def test_sanity(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data,
                         {'average_grading_points_given': '1.00',
                          'user_name': 'Test User'})

    def test_assignment_grading_average_sanity(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period,
                                max_points=50,
                                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=25)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data,
                         {'average_grading_points_given': '25.00',
                          'user_name': 'Test User'})

    def test_assignment_multiple_groups_grading_average_sanity(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment',
                                parentnode=period, max_points=10,
                                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=5)
        self.__make_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=10)
        self.__make_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=15)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data,
                         {'average_grading_points_given': '10.00',
                          'user_name': 'Test User'})

    def test_assignment_grading_average_only_for_relatedexaminer_id_passed(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment',
                                parentnode=period, max_points=10,
                                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)
        relatedexaminer1 = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User 1')
        relatedexaminer2 = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User 2')
        self.__make_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer1, grading_points=5)
        self.__make_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer2, grading_points=10)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer1.id})
        self.assertEqual(response.data,
                         {'average_grading_points_given': '5.00',
                          'user_name': 'Test User 1'})
