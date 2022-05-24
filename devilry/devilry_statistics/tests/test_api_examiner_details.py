from django import test
from django.utils import timezone
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.utils.api import api_test_mixin
from devilry.devilry_statistics.api.assignment import examiner_details
from devilry.devilry_group import devilry_group_baker_factories as group_baker


class TestExaminerDetailsApi(test.TestCase, api_test_mixin.ApiTestMixin):
    apiview_class = examiner_details.ExaminerDetailsApi

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __make_published_group_for_relatedexaminer(self, assignment, relatedexaminer, grading_points,
                                                   feedbackset_deadline_datetime=None):
        if feedbackset_deadline_datetime is None:
            feedbackset_deadline_datetime = timezone.now()
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=group)
        group_baker.feedbackset_first_attempt_published(group=group, grading_points=grading_points,
                                                        deadline_datetime=feedbackset_deadline_datetime)
        return group

    def __make_unpublished_group_for_relatedexaminer(self, assignment, relatedexaminer,
                                                     feedbackset_deadline_datetime=None):
        if feedbackset_deadline_datetime is None:
            feedbackset_deadline_datetime = timezone.now()
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=group)
        group_baker.feedbackset_first_attempt_unpublished(group=group, deadline_datetime=feedbackset_deadline_datetime)
        return group

    def test_user_not_authenticated(self):
        response = self.make_get_request()
        self.assertEqual(response.status_code, 403)

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
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
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
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
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
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
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

    def test_total_group_count(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_unpublished_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer)
        self.__make_unpublished_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer)
        self.__make_unpublished_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['total_group_count'], 3)

    def test_groups_corrected_count_none(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_unpublished_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['groups_corrected_count'], 0)

    def test_groups_corrected_count_multiple(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=0)
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['groups_corrected_count'], 3)

    def test_groups_with_passing_grade_count_none(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=0)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['groups_with_passing_grade_count'], 0)

    def test_groups_with_passing_grade_count_multiple(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=0)
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['groups_with_passing_grade_count'], 2)

    def test_groups_with_failing_grade_count_none(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['groups_with_failing_grade_count'], 0)

    def test_groups_with_failing_grade_count_multiple(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=0)
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=0)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['groups_with_failing_grade_count'], 2)

    def test_groups_waiting_for_feedback_count_none(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1,
            feedbackset_deadline_datetime=timezone.now() - timezone.timedelta(days=1))

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['groups_waiting_for_feedback_count'], 0)

    def test_groups_waiting_for_feedback_count_multiple(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        now = timezone.now()
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1,
            feedbackset_deadline_datetime=now - timezone.timedelta(days=1))
        self.__make_unpublished_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer,
            feedbackset_deadline_datetime=now - timezone.timedelta(days=1))
        self.__make_unpublished_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer,
            feedbackset_deadline_datetime=now - timezone.timedelta(days=1))

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['groups_waiting_for_feedback_count'], 2)

    def test_groups_waiting_for_deadline_to_expire_none(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1,
            feedbackset_deadline_datetime=timezone.now() - timezone.timedelta(days=1))

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['groups_waiting_for_deadline_to_expire_count'], 0)

    def test_groups_waiting_for_deadline_to_expire_multiple(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        now = timezone.now()
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1,
            feedbackset_deadline_datetime=now - timezone.timedelta(days=1))
        self.__make_unpublished_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer,
            feedbackset_deadline_datetime=now + timezone.timedelta(days=1))
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1,
            feedbackset_deadline_datetime=now + timezone.timedelta(days=1))
        self.__make_unpublished_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer,
            feedbackset_deadline_datetime=now + timezone.timedelta(days=1))

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['groups_waiting_for_deadline_to_expire_count'], 2)

    def test_points_average_highest_lowest(self):
        period = baker.make('core.Period')
        assignment = baker.make('core.Assignment', parentnode=period,
                                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
                                max_points=50)
        relatedexaminer = baker.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=5)
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=15)
        self.__make_published_group_for_relatedexaminer(
            assignment=assignment, relatedexaminer=relatedexaminer, grading_points=10)
        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.data['points_average'], '10.00')
        self.assertEqual(response.data['points_highest'], '15.00')
        self.assertEqual(response.data['points_lowest'], '5.00')
