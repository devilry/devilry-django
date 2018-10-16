from django import test
from model_mommy import mommy

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_statistics.tests.test_api import api_test_mixin
from devilry.devilry_statistics.api.assignment import examiner_group_results
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy


class TestExaminerAverageGradingPointsApi(test.TestCase, api_test_mixin.ApiTestMixin):
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
