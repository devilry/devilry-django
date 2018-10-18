from django import test
from model_mommy import mommy

from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_statistics.tests.test_api import api_test_mixin
from devilry.devilry_statistics.api.assignment import examiner_group_results
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy


class TestExaminerGroupResultsApi(test.TestCase, api_test_mixin.ApiTestMixin):
    apiview_class = examiner_group_results.ExaminerGroupResultApi

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __make_published_group_for_relatedexaminer(self, assignment, relatedexaminer, grading_points):
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=group)
        group_mommy.feedbackset_first_attempt_published(group=group, grading_points=grading_points)
        return group

    def __make_unpublished_group_for_relatedexaminer(self, assignment, relatedexaminer):
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=group)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        return group

    def test_user_not_authenticated(self):
        response = self.make_get_request()
        self.assertEqual(response.status_code, 403)

    def test_user_has_no_access(self):
        assignment = mommy.make('core.Assignment')
        relatedexaminer = mommy.make('core.RelatedExaminer', user__fullname='Test User')
        response = self.make_get_request(
            requestuser=self.make_user(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.status_code, 403)

    def test_period_admin_on_different_period_does_not_have_access(self):
        other_period = mommy.make('core.Period')
        period = mommy.make('core.Period')
        assignment = mommy.make('core.Assignment', parentnode=period)
        requestuser = self.make_user()
        permissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                     period=other_period)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=requestuser,
                   permissiongroup=permissiongroup.permissiongroup)
        response = self.make_get_request(
            requestuser=requestuser,
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': 1})
        self.assertEqual(response.status_code, 403)

    def test_period_admin_has_access(self):
        period = mommy.make('core.Period')
        assignment = mommy.make('core.Assignment', parentnode=period)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
        requestuser = self.make_user()
        permissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                     period=period)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=requestuser,
                   permissiongroup=permissiongroup.permissiongroup)
        response = self.make_get_request(
            requestuser=requestuser,
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.status_code, 200)

    def test_subject_admin_on_different_subject_does_not_have_access(self):
        other_subject = mommy.make('core.Subject')
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        assignment = mommy.make('core.Assignment', parentnode=period)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        requestuser = self.make_user()
        permissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                     subject=other_subject)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=requestuser,
                   permissiongroup=permissiongroup.permissiongroup)
        response = self.make_get_request(
            requestuser=requestuser,
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.status_code, 403)

    def test_subject_admin_has_access(self):
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        assignment = mommy.make('core.Assignment', parentnode=period)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
        requestuser = self.make_user()
        permissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                     permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                     subject=subject)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=requestuser,
                   permissiongroup=permissiongroup.permissiongroup)
        response = self.make_get_request(
            requestuser=requestuser,
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.status_code, 200)

    def test_department_admin_has_access(self):
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        assignment = mommy.make('core.Assignment', parentnode=period)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer, grading_points=1)
        requestuser = self.make_user()
        permissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                     subject=subject, permissiongroup__grouptype='departmentadmin')
        mommy.make('devilry_account.PermissionGroupUser',
                   user=requestuser,
                   permissiongroup=permissiongroup.permissiongroup)
        response = self.make_get_request(
            requestuser=requestuser,
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(response.status_code, 200)

    def calculate_percentage(self, p, total):
        if p == 0 or total == 0:
            return 0
        return 100 * (float(p) / float(total))

    def test_sanity(self):
        period = mommy.make('core.Period')
        assignment = mommy.make('core.Assignment', parentnode=period)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer,
                                                        grading_points=1)
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer,
                                                        grading_points=0)
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer,
                                                        grading_points=0)
        self.__make_unpublished_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer)
        self.__make_unpublished_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer)
        self.__make_unpublished_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer)

        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(
            response.data,
            {
                'groups_passed': '{0:.2f}'.format(self.calculate_percentage(p=1, total=6)),
                'groups_failed': '{0:.2f}'.format(self.calculate_percentage(p=2, total=6)),
                'groups_not_corrected': '{0:.2f}'.format(self.calculate_percentage(p=3, total=6)),
                'user_name': 'Test User'
            })

    def test_single_group_passed(self):
        period = mommy.make('core.Period')
        assignment = mommy.make('core.Assignment', parentnode=period)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer,
                                                        grading_points=1)
        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(
            response.data,
            {
                'groups_passed': '100.00',
                'groups_failed': '0.00',
                'groups_not_corrected': '0.00',
                'user_name': 'Test User'
            })

    def test_single_group_failed(self):
        period = mommy.make('core.Period')
        assignment = mommy.make('core.Assignment', parentnode=period)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer,
                                                        grading_points=0)
        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(
            response.data,
            {
                'groups_passed': '0.00',
                'groups_failed': '100.00',
                'groups_not_corrected': '0.00',
                'user_name': 'Test User'
            })

    def test_single_group_not_corrected(self):
        period = mommy.make('core.Period')
        assignment = mommy.make('core.Assignment', parentnode=period)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_unpublished_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer)
        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(
            response.data,
            {
                'groups_passed': '0.00',
                'groups_failed': '0.00',
                'groups_not_corrected': '100.00',
                'user_name': 'Test User'
            })

    def test_equally_many_passed_failed_not_corrected(self):
        period = mommy.make('core.Period')
        assignment = mommy.make('core.Assignment', parentnode=period)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer,
                                                        grading_points=1)
        self.__make_published_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer,
                                                        grading_points=0)
        self.__make_unpublished_group_for_relatedexaminer(assignment=assignment, relatedexaminer=relatedexaminer)
        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(
            response.data,
            {
                'groups_passed': '33.33',
                'groups_failed': '33.33',
                'groups_not_corrected': '33.33',
                'user_name': 'Test User'
            })

    def test_relatedexaminer_no_groups_sanity(self):
        period = mommy.make('core.Period')
        assignment = mommy.make('core.Assignment', parentnode=period)
        relatedexaminer = mommy.make('core.RelatedExaminer', period=period, user__fullname='Test User')
        response = self.make_get_request(
            requestuser=self.make_superuser(),
            viewkwargs={'assignment_id': assignment.id, 'relatedexaminer_id': relatedexaminer.id})
        self.assertEqual(
            response.data,
            {
                'groups_passed': '0.00',
                'groups_failed': '0.00',
                'groups_not_corrected': '0.00',
                'user_name': 'Test User'
            })
