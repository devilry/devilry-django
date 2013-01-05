from django.test import TestCase
from devilry.apps.core.testhelper import TestHelper
from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment


class GroupsGroupedByRelatedStudentAndAssignmentTest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()

        self.testhelper.add(nodes="uni",
            subjects=["sub"],
            periods=["p1:begins(-24):ends(6)"],
            assignments=['a1:pub(1)', 'a3:pub(4)', 'a2:pub(3)'],
            assignmentgroups=["stud1:candidate(student1):examiner(examiner1)",
                              "stud2:candidate(student2):examiner(examiner1)",
                              "stud3:candidate(student3):examiner(examiner1)",
                              "stud4:candidate(student4,student3):examiner(examiner1)"],
            deadlines=['d1:ends(1)'])

    def _add_good_feedback(self, group):
        delivery = self.testhelper.add_delivery(group, {"good.py": "print awesome"})
        self.testhelper.add_feedback(delivery, {'grade': '100/100', 'points': 100, 'is_passing_grade': True})

    def _add_bad_feedback(self, group):
        delivery = self.testhelper.add_delivery(group, {"bad.py": "print bad"})
        self.testhelper.add_feedback(delivery, {'grade': '0/100', 'points': 0, 'is_passing_grade': False})


    def test_iter_assignments(self):
        grouper = GroupsGroupedByRelatedStudentAndAssignment(self.testhelper.sub_p1)
        shortnames = [assignment.short_name for assignment in grouper.iter_assignments()]
        self.assertEquals(shortnames, ['a1', 'a2', 'a3'])

    def test_iter_students_that_is_candidate_but_not_in_related_none(self):
        grouper = GroupsGroupedByRelatedStudentAndAssignment(self.testhelper.sub_p1)
        self.assertEqual(len(list(grouper.iter_relatedstudents_with_results())), 0)

    def test_iter_students_that_is_candidate_but_not_in_related(self):
        grouper = GroupsGroupedByRelatedStudentAndAssignment(self.testhelper.sub_p1)
        ignored = list(grouper.iter_students_that_is_candidate_but_not_in_related())
        self.assertEquals(len(ignored), 4)
        student1_info = None
        for aggregated_relstudentinfo in ignored:
            if aggregated_relstudentinfo.user == self.testhelper.student1:
                student1_info = aggregated_relstudentinfo
                break
        grouplists = list(student1_info.iter_groups_by_assignment())
        self.assertEquals(len(grouplists), 3) # Should match the number of assignments
        self.assertEquals(len(grouplists[0]), 1)
        self.assertEquals(grouplists[0][0].feedback, None)

    def test_iter_students_with_feedback_that_is_candidate_but_not_in_related_none(self):
        grouper = GroupsGroupedByRelatedStudentAndAssignment(self.testhelper.sub_p1)
        self.assertEquals(len(list(grouper.iter_students_with_feedback_that_is_candidate_but_not_in_related())), 0)
        self.assertEquals(len(list(grouper.iter_relatedstudents_with_results())), 0)

    def test_iter_students_with_feedback_that_is_candidate_but_not_in_related(self):
        self._add_bad_feedback(self.testhelper.sub_p1_a1_stud1)
        grouper = GroupsGroupedByRelatedStudentAndAssignment(self.testhelper.sub_p1)
        ignored = list(grouper.iter_students_with_feedback_that_is_candidate_but_not_in_related())
        self.assertEquals(len(ignored), 1)
        grouplists = list(ignored[0].iter_groups_by_assignment())
        self.assertEquals(len(grouplists), 3) # Should match the number of assignments
        self.assertEquals(grouplists[0][0].feedback.grade, '0/100')

    def test_iter_relatedstudents_with_results(self):
        self._add_bad_feedback(self.testhelper.sub_p1_a1_stud1)
        self.testhelper.sub_p1.relatedstudent_set.create(user=self.testhelper.student1)
        grouper = GroupsGroupedByRelatedStudentAndAssignment(self.testhelper.sub_p1)
        results = list(grouper.iter_relatedstudents_with_results())
        self.assertEqual(len(results), 1)
        student1info = results[0]
        grouplists = list(student1info.iter_groups_by_assignment())
        self.assertEqual(len(grouplists), 3)  # Should match the number of assignments
        self.assertEqual(grouplists[0].get_best_gradestring(), '0/100')

    def test_iter_relatedstudents_with_results_multi(self):
        self.testhelper.sub_p1.relatedstudent_set.create(user=self.testhelper.student1)
        self.testhelper.sub_p1.relatedstudent_set.create(user=self.testhelper.student2)
        grouper = GroupsGroupedByRelatedStudentAndAssignment(self.testhelper.sub_p1)
        results = list(grouper.iter_relatedstudents_with_results())
        self.assertEqual(len(results), 2)