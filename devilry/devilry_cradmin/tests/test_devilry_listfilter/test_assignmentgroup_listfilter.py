from django import test

from model_bakery import baker

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_cradmin.devilry_listfilter.assignmentgroup import ExaminerCountFilter, CandidateCountFilter


class TestExaminerCountFilter(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.testgroup0 = self.__create_group_with_examiners(num_examiners=0)
        self.testgroup1 = self.__create_group_with_examiners(num_examiners=1)
        self.testgroup2 = self.__create_group_with_examiners(num_examiners=2)
        self.testgroup3 = self.__create_group_with_examiners(num_examiners=3)
        self.testgroup4 = self.__create_group_with_examiners(num_examiners=4)
        self.testgroup5 = self.__create_group_with_examiners(num_examiners=5)
        self.testgroup6 = self.__create_group_with_examiners(num_examiners=6)
        self.testgroup7 = self.__create_group_with_examiners(num_examiners=7)

    def __create_group_with_examiners(self, num_examiners=0):
        assignment_group = baker.make('core.AssignmentGroup')
        for num in range(num_examiners):
            baker.make('core.Examiner', assignmentgroup=assignment_group)
        return assignment_group

    def __filter_examiners(self, filter_value):
        queryset = AssignmentGroup.objects.all()
        examinercountfilter = ExaminerCountFilter()
        examinercountfilter.values = [filter_value]
        return examinercountfilter.filter(queryobject=queryset)

    def test_exact_0(self):
        filtered_queryset = self.__filter_examiners(filter_value='eq-0')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup0.id)

    def test_exact_1(self):
        filtered_queryset = self.__filter_examiners(filter_value='eq-1')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup1.id)

    def test_exact_2(self):
        filtered_queryset = self.__filter_examiners(filter_value='eq-2')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup2.id)

    def test_exact_3(self):
        filtered_queryset = self.__filter_examiners(filter_value='eq-3')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup3.id)

    def test_exact_4(self):
        filtered_queryset = self.__filter_examiners(filter_value='eq-4')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup4.id)

    def test_exact_5(self):
        filtered_queryset = self.__filter_examiners(filter_value='eq-5')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup5.id)

    def test_exact_6(self):
        filtered_queryset = self.__filter_examiners(filter_value='eq-6')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup6.id)

    def test_less_than_2(self):
        filtered_queryset = self.__filter_examiners(filter_value='lt-2')
        self.assertEqual(filtered_queryset.count(), 2)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)

    def test_less_than_3(self):
        filtered_queryset = self.__filter_examiners(filter_value='lt-3')
        self.assertEqual(filtered_queryset.count(), 3)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)

    def test_less_than_4(self):
        filtered_queryset = self.__filter_examiners(filter_value='lt-4')
        self.assertEqual(filtered_queryset.count(), 4)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)

    def test_less_than_5(self):
        filtered_queryset = self.__filter_examiners(filter_value='lt-5')
        self.assertEqual(filtered_queryset.count(), 5)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)

    def test_less_than_6(self):
        filtered_queryset = self.__filter_examiners(filter_value='lt-6')
        self.assertEqual(filtered_queryset.count(), 6)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)

    def test_greater_than_0(self):
        filtered_queryset = self.__filter_examiners(filter_value='gt-0')
        self.assertEqual(filtered_queryset.count(), 7)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_1(self):
        filtered_queryset = self.__filter_examiners(filter_value='gt-1')
        self.assertEqual(filtered_queryset.count(), 6)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_2(self):
        filtered_queryset = self.__filter_examiners(filter_value='gt-2')
        self.assertEqual(filtered_queryset.count(), 5)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertNotIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_3(self):
        filtered_queryset = self.__filter_examiners(filter_value='gt-3')
        self.assertEqual(filtered_queryset.count(), 4)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertNotIn(self.testgroup2.id, filtered_group_ids)
        self.assertNotIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_4(self):
        filtered_queryset = self.__filter_examiners(filter_value='gt-4')
        self.assertEqual(filtered_queryset.count(), 3)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertNotIn(self.testgroup2.id, filtered_group_ids)
        self.assertNotIn(self.testgroup3.id, filtered_group_ids)
        self.assertNotIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_5(self):
        filtered_queryset = self.__filter_examiners(filter_value='gt-5')
        self.assertEqual(filtered_queryset.count(), 2)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertNotIn(self.testgroup2.id, filtered_group_ids)
        self.assertNotIn(self.testgroup3.id, filtered_group_ids)
        self.assertNotIn(self.testgroup4.id, filtered_group_ids)
        self.assertNotIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_6(self):
        filtered_queryset = self.__filter_examiners(filter_value='gt-6')
        self.assertEqual(filtered_queryset.count(), 1)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertNotIn(self.testgroup2.id, filtered_group_ids)
        self.assertNotIn(self.testgroup3.id, filtered_group_ids)
        self.assertNotIn(self.testgroup4.id, filtered_group_ids)
        self.assertNotIn(self.testgroup5.id, filtered_group_ids)
        self.assertNotIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_invalid_filter_value(self):
        filtered_queryset = self.__filter_examiners(filter_value='gt-7')
        self.assertEqual(filtered_queryset.count(), 0)


class TestCandidateCountFilter(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.testgroup0 = self.__create_group_with_candidates(num_candidates=0)
        self.testgroup1 = self.__create_group_with_candidates(num_candidates=1)
        self.testgroup2 = self.__create_group_with_candidates(num_candidates=2)
        self.testgroup3 = self.__create_group_with_candidates(num_candidates=3)
        self.testgroup4 = self.__create_group_with_candidates(num_candidates=4)
        self.testgroup5 = self.__create_group_with_candidates(num_candidates=5)
        self.testgroup6 = self.__create_group_with_candidates(num_candidates=6)
        self.testgroup7 = self.__create_group_with_candidates(num_candidates=7)

    def __create_group_with_candidates(self, num_candidates=0):
        assignment_group = baker.make('core.AssignmentGroup')
        for num in range(num_candidates):
            baker.make('core.Candidate', assignment_group=assignment_group)
        return assignment_group

    def __filter_candidates(self, filter_value):
        queryset = AssignmentGroup.objects.all()
        candidatecountfilter = CandidateCountFilter()
        candidatecountfilter.values = [filter_value]
        return candidatecountfilter.filter(queryobject=queryset)

    def test_exact_1(self):
        filtered_queryset = self.__filter_candidates(filter_value='eq-1')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup1.id)

    def test_exact_2(self):
        filtered_queryset = self.__filter_candidates(filter_value='eq-2')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup2.id)

    def test_exact_3(self):
        filtered_queryset = self.__filter_candidates(filter_value='eq-3')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup3.id)

    def test_exact_4(self):
        filtered_queryset = self.__filter_candidates(filter_value='eq-4')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup4.id)

    def test_exact_5(self):
        filtered_queryset = self.__filter_candidates(filter_value='eq-5')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup5.id)

    def test_exact_6(self):
        filtered_queryset = self.__filter_candidates(filter_value='eq-6')
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset[0].id, self.testgroup6.id)

    def test_less_than_2(self):
        filtered_queryset = self.__filter_candidates(filter_value='lt-2')
        self.assertEqual(filtered_queryset.count(), 2)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)

    def test_less_than_3(self):
        filtered_queryset = self.__filter_candidates(filter_value='lt-3')
        self.assertEqual(filtered_queryset.count(), 3)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)

    def test_less_than_4(self):
        filtered_queryset = self.__filter_candidates(filter_value='lt-4')
        self.assertEqual(filtered_queryset.count(), 4)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)

    def test_less_than_5(self):
        filtered_queryset = self.__filter_candidates(filter_value='lt-5')
        self.assertEqual(filtered_queryset.count(), 5)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)

    def test_less_than_6(self):
        filtered_queryset = self.__filter_candidates(filter_value='lt-6')
        self.assertEqual(filtered_queryset.count(), 6)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)

    def test_greater_than_0(self):
        filtered_queryset = self.__filter_candidates(filter_value='gt-0')
        self.assertEqual(filtered_queryset.count(), 7)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_1(self):
        filtered_queryset = self.__filter_candidates(filter_value='gt-1')
        self.assertEqual(filtered_queryset.count(), 6)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_2(self):
        filtered_queryset = self.__filter_candidates(filter_value='gt-2')
        self.assertEqual(filtered_queryset.count(), 5)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertNotIn(self.testgroup2.id, filtered_group_ids)
        self.assertIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_3(self):
        filtered_queryset = self.__filter_candidates(filter_value='gt-3')
        self.assertEqual(filtered_queryset.count(), 4)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertNotIn(self.testgroup2.id, filtered_group_ids)
        self.assertNotIn(self.testgroup3.id, filtered_group_ids)
        self.assertIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_4(self):
        filtered_queryset = self.__filter_candidates(filter_value='gt-4')
        self.assertEqual(filtered_queryset.count(), 3)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertNotIn(self.testgroup2.id, filtered_group_ids)
        self.assertNotIn(self.testgroup3.id, filtered_group_ids)
        self.assertNotIn(self.testgroup4.id, filtered_group_ids)
        self.assertIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_5(self):
        filtered_queryset = self.__filter_candidates(filter_value='gt-5')
        self.assertEqual(filtered_queryset.count(), 2)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertNotIn(self.testgroup2.id, filtered_group_ids)
        self.assertNotIn(self.testgroup3.id, filtered_group_ids)
        self.assertNotIn(self.testgroup4.id, filtered_group_ids)
        self.assertNotIn(self.testgroup5.id, filtered_group_ids)
        self.assertIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)

    def test_greater_than_6(self):
        filtered_queryset = self.__filter_candidates(filter_value='gt-6')
        self.assertEqual(filtered_queryset.count(), 1)
        filtered_group_ids = [group.id for group in filtered_queryset]
        self.assertNotIn(self.testgroup0.id, filtered_group_ids)
        self.assertNotIn(self.testgroup1.id, filtered_group_ids)
        self.assertNotIn(self.testgroup2.id, filtered_group_ids)
        self.assertNotIn(self.testgroup3.id, filtered_group_ids)
        self.assertNotIn(self.testgroup4.id, filtered_group_ids)
        self.assertNotIn(self.testgroup5.id, filtered_group_ids)
        self.assertNotIn(self.testgroup6.id, filtered_group_ids)
        self.assertIn(self.testgroup7.id, filtered_group_ids)
