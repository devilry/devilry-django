from datetime import datetime
from django.test import TestCase
from devilry.apps.core.testhelper import TestHelper

from ..passed_in_previous_period import MarkAsPassedInPreviousPeriod
from ..passed_in_previous_period import OnlyFailingInPrevious
from ..passed_in_previous_period import NotInPrevious
from ..passed_in_previous_period import HasFeedback
from ..passed_in_previous_period import PassingGradeOnlyInMultiCandidateGroups


class TestMarkAsPassedInPrevious(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()

        # 2 Years ago, student1 and the group with student 2 and 3 passed
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p1:begins(-24):ends(6)"],
                            assignments=["a1"],
                            assignmentgroups=["stud1:candidate(student1):examiner(examiner1)",
                                              "stud2:candidate(student2):examiner(examiner1)",
                                              "stud3and4:candidate(student3,student4):examiner(examiner1)",
                                              "stud5:candidate(student5):examiner(examiner1)"],
                            deadlines=['d1:ends(1)'])
        for group in self.testhelper.sub_p1_a1.assignmentgroups.all():
            if group.name in ('stud1', 'stud3and4'):
                delivery = self.testhelper.add_delivery(group, {"good.py": "print awesome"})
                self.testhelper.add_feedback(delivery, {'grade': 'p1Passed', 'points': 100, 'is_passing_grade': True},
                                             rendered_view='P1 good')
            else:
                delivery = self.testhelper.add_delivery(group, {"bad.py": "print bad"})
                self.testhelper.add_feedback(delivery, {'grade': 'p1Failed', 'points': 0, 'is_passing_grade': False})

        # 1 Year ago, student2 and student5 passed
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p2:begins(-12):ends(6)"],
                            assignments=["a1"],
                            assignmentgroups=["stud1:candidate(student1):examiner(examiner1)",
                                              "stud2:candidate(student2):examiner(examiner1)",
                                              "stud3and4:candidate(student3,student4):examiner(examiner1)",
                                              "stud5:candidate(student5):examiner(examiner1)",
                                              "studfail:candidate(studentfail):examiner(examiner1)"],
                            deadlines=['d1:ends(1)'])
        for group in self.testhelper.sub_p2_a1.assignmentgroups.all():
            if group.name in ('stud2', 'stud5'):
                delivery = self.testhelper.add_delivery(group, {"good.py": "print awesome"})
                self.testhelper.add_feedback(delivery, {'grade': 'p2Passed', 'points': 200, 'is_passing_grade': True})
            else:
                delivery = self.testhelper.add_delivery(group, {"bad.py": "print bad"})
                self.testhelper.add_feedback(delivery, {'grade': 'p2Failed', 'points': 10, 'is_passing_grade': False})

    def test_mark_group(self):
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p3:begins(-2):ends(6)"],
                            assignments=["a1"],
                            assignmentgroups=["g1:candidate(student1):examiner(examiner1)"],
                            deadlines=['d1:ends(1)'])
        assignment = self.testhelper.sub_p3_a1
        marker = MarkAsPassedInPreviousPeriod(assignment)
        group = self.testhelper.sub_p3_a1_g1
        marker.mark_group(group)
        delivery = group.deadlines.all()[0].deliveries.all()[0]
        self.assertEquals(delivery.alias_delivery,
                          self.testhelper.sub_p1_a1_stud1_d1.deliveries.all()[0])
        self.assertEquals(delivery.delivery_type, 2) # Alias
        feedback = delivery.feedbacks.all()[0]
        self.assertTrue(feedback.is_passing_grade)
        self.assertEquals(feedback.grade, 'p1Passed')
        self.assertEquals(feedback.points, 100)
        self.assertEquals(feedback.rendered_view, 'P1 good')

    def test_mark_group_prioritize_newest(self):
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p3:begins(-2):ends(6)"],
                            assignments=["a1"],
                            assignmentgroups=["group:candidate(student2):examiner(examiner1)"],
                            deadlines=['d1:ends(1)'])
        assignment = self.testhelper.sub_p3_a1
        marker = MarkAsPassedInPreviousPeriod(assignment)
        group = self.testhelper.sub_p3_a1_group
        marker.mark_group(group)
        delivery = group.deadlines.all()[0].deliveries.all()[0]
        self.assertEquals(delivery.alias_delivery,
                          self.testhelper.sub_p2_a1_stud2_d1.deliveries.all()[0])

    def test_mark_group_only_failing_in_previous(self):
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p3:begins(-2):ends(6)"],
                            assignments=["a1"],
                            assignmentgroups=["group:candidate(studentfail):examiner(examiner1)"],
                            deadlines=['d1:ends(1)'])
        assignment = self.testhelper.sub_p3_a1
        marker = MarkAsPassedInPreviousPeriod(assignment)
        group = self.testhelper.sub_p3_a1_group
        with self.assertRaises(OnlyFailingInPrevious):
            marker.mark_group(group)

    def test_mark_group_not_in_previous(self):
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p3:begins(-2):ends(6)"],
                            assignments=["a1"],
                            assignmentgroups=["group:candidate(studentnew):examiner(examiner1)"],
                            deadlines=['d1:ends(1)'])
        assignment = self.testhelper.sub_p3_a1
        marker = MarkAsPassedInPreviousPeriod(assignment)
        group = self.testhelper.sub_p3_a1_group
        with self.assertRaises(NotInPrevious):
            marker.mark_group(group)

    def test_mark_multistudent_group_source(self):
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p3:begins(-2):ends(6)"],
                            assignments=["a1"],
                            assignmentgroups=["group:candidate(student4):examiner(examiner1)"], # Student4 is in a group with student3 on p1.a1
                            deadlines=['d1:ends(1)'])
        assignment = self.testhelper.sub_p3_a1
        marker = MarkAsPassedInPreviousPeriod(assignment)
        group = self.testhelper.sub_p3_a1_group
        with self.assertRaises(PassingGradeOnlyInMultiCandidateGroups):
            marker.mark_group(group)

    def test_mark_group_manually(self):
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p3:begins(-2):ends(6)"],
                            assignments=["a1"],
                            assignmentgroups=["g1:candidate(student1):examiner(examiner1)"],
                            deadlines=['d1:ends(1)'])
        assignment = self.testhelper.sub_p3_a1
        marker = MarkAsPassedInPreviousPeriod(assignment)
        group = self.testhelper.sub_p3_a1_g1
        marker.mark_group(group, feedback={'grade': 'A',
                                           'is_passing_grade': True,
                                           'points': 100,
                                           'rendered_view': 'Test',
                                           'saved_by': self.testhelper.examiner1})
        delivery = group.deadlines.all()[0].deliveries.all()[0]
        self.assertEquals(delivery.alias_delivery, None)
        self.assertEquals(delivery.delivery_type, 2) # Alias
        feedback = delivery.feedbacks.all()[0]
        self.assertTrue(feedback.is_passing_grade)
        self.assertEquals(feedback.grade, 'A')
        self.assertEquals(feedback.points, 100)
        self.assertEquals(feedback.rendered_view, 'Test')

    def test_has_feedback(self):
        assignment = self.testhelper.sub_p2_a1
        marker = MarkAsPassedInPreviousPeriod(assignment)
        group = self.testhelper.sub_p2_a1_stud2
        with self.assertRaises(HasFeedback):
            marker.find_previously_passed_group(group)

    def test_mark_all(self):
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p3:begins(-2):ends(6)"],
                            assignments=["a1"],
                            assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
                                              "g2:candidate(student2):examiner(examiner1)",
                                              "g3:candidate(student3):examiner(examiner1)",
                                              "g4:candidate(student4):examiner(examiner1)",
                                              "g5:candidate(student5):examiner(examiner1)",
                                              "g6:candidate(student6):examiner(examiner1)" # student6 is not in any of the previous semesters, and should not be touched
                                             ],
                            deadlines=['d1:ends(1)'])
        assignment = self.testhelper.sub_p3_a1
        marker = MarkAsPassedInPreviousPeriod(assignment)
        results = marker.mark_all()
        self.assertEquals(set(results['marked']),
                          set([(self.testhelper.sub_p3_a1_g1, self.testhelper.sub_p1_a1_stud1),
                               (self.testhelper.sub_p3_a1_g2, self.testhelper.sub_p2_a1_stud2),
                               (self.testhelper.sub_p3_a1_g5, self.testhelper.sub_p2_a1_stud5)]))
        self.assertEquals(set(results['ignored']['not_in_previous']),
                          set([self.testhelper.sub_p3_a1_g6]))
        self.assertEquals(set(results['ignored']['only_multicandidategroups_passed']),
                          set([self.testhelper.sub_p3_a1_g3,
                               self.testhelper.sub_p3_a1_g4]))
        g2 = self.testhelper.sub_p3_a1_g2
        delivery = g2.deadlines.all()[0].deliveries.all()[0]
        self.assertEquals(delivery.alias_delivery,
                          self.testhelper.sub_p2_a1_stud2_d1.deliveries.all()[0])


    def test_mark_all_pretend(self):
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p3:begins(-2):ends(6)"],
                            assignments=["a1"],
                            assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
                                              "g2:candidate(student2):examiner(examiner1)",
                                              "g3:candidate(student3):examiner(examiner1)",
                                              "g4:candidate(student4):examiner(examiner1)",
                                              "g5:candidate(student5):examiner(examiner1)",
                                              "g6:candidate(student6):examiner(examiner1)" # student6 is not in any of the previous semesters, and should not be touched
                                             ],
                            deadlines=['d1:ends(1)'])
        assignment = self.testhelper.sub_p3_a1
        marker = MarkAsPassedInPreviousPeriod(assignment)
        results = marker.mark_all(pretend=True)
        self.assertEquals(set(results['marked']),
                          set([(self.testhelper.sub_p3_a1_g1, self.testhelper.sub_p1_a1_stud1),
                               (self.testhelper.sub_p3_a1_g2, self.testhelper.sub_p2_a1_stud2),
                               (self.testhelper.sub_p3_a1_g5, self.testhelper.sub_p2_a1_stud5)]))
        self.assertEquals(set(results['ignored']['not_in_previous']),
                          set([self.testhelper.sub_p3_a1_g6]))
        self.assertEquals(set(results['ignored']['only_multicandidategroups_passed']),
                          set([self.testhelper.sub_p3_a1_g3,
                               self.testhelper.sub_p3_a1_g4]))
        g2 = self.testhelper.sub_p3_a1_g2
        self.assertEquals(g2.deadlines.all()[0].deliveries.count(), 0)


    def test_mark_group_past_deadline(self):
        self.testhelper.add(nodes="uni",
                            subjects=["sub"],
                            periods=["p3:begins(-3):ends(6)"],
                            assignments=["a1:pub(1)"],
                            assignmentgroups=["group:candidate(student1):examiner(examiner1)"],
                            deadlines=['d1:ends(1)'])
        assignment = self.testhelper.sub_p3_a1
        marker = MarkAsPassedInPreviousPeriod(assignment)
        group = self.testhelper.sub_p3_a1_group
        self.assertEquals(len(group.deadlines.all()), 1)
        self.assertTrue(group.deadlines.all()[0].deadline < datetime.now())
        marker.mark_group(group)
        self.assertEquals(len(group.deadlines.all()), 1)
        self.assertTrue(group.deadlines.all()[0].deadline >= datetime.now())
