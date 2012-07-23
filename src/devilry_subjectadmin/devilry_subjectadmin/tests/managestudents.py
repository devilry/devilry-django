from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import Subject

from .base import SubjectAdminSeleniumTestCase


class TestManageStudents(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1:admin(a1admin)'])

    def setUpStudentsBasic(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student2)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g3:candidate(student3)')

    def setUpStudentsFull(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1).dl:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student2):examiner(examiner1).dl:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g3:candidate(student3):examiner(examiner1).dl:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g4:candidate(student4):examiner(examiner1).dl:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g5:candidate(student5):examiner(examiner1).dl:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g6:candidate(student6):examiner(examiner1).dl:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g7:candidate(student7)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g8:candidate(student8)')

        goodFile = {'good.py': ['print ', 'awesome']}
        okFile = {'ok.py': ['print ', 'meh']}
        badFile = {'bad.py': ['print ', 'bah']}

        self.testhelper.add_delivery('uni;sub.p1.a1.g1', badFile)
        self.testhelper.add_delivery('uni;sub.p1.a1.g1', okFile)
        self.testhelper.add_delivery('uni;sub.p1.a1.g1', goodFile)
        self.testhelper.add_delivery('uni;sub.p1.a1.g2', badFile)
        self.testhelper.add_delivery('uni;sub.p1.a1.g2', goodFile)
        self.testhelper.add_delivery('uni;sub.p1.a1.g3', okFile)
        self.testhelper.add_delivery('uni;sub.p1.a1.g4', badFile)
        self.testhelper.add_delivery('uni;sub.p1.a1.g5', badFile)
        self.testhelper.add_delivery('uni;sub.p1.a1.g6', badFile)

        goodVerdict = None
        okVerdict = {'grade': 'C', 'points': 85, 'is_passing_grade': True}
        badVerdict = {'grade': 'E', 'points': 60, 'is_passing_grade': True}
        failVerdict = {'grade': 'F', 'points': 30, 'is_passing_grade': False}

        self.testhelper.add_feedback('uni;sub.p1.a1.g1', verdict=goodVerdict)
        self.testhelper.add_feedback('uni;sub.p1.a1.g3', verdict=okVerdict)
        self.testhelper.add_feedback('uni;sub.p1.a1.g4', verdict=badVerdict)
        self.testhelper.add_feedback('uni;sub.p1.a1.g5', verdict=failVerdict)

    def _browseToManagestudentsAs(self, username, assignment):
        self.login(username)
        self.browseTo('/assignment/{0}/@@manage-students/'.format(assignment.id))

    def test_listlength(self):
        self.setUpStudentsFull()
        self._browseToManagestudentsAs('a1admin', self.testhelper.sub_p1_a1)
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsoverview', timeout=20)

        self.waitForCssSelector('.devilry_subjectadmin_listofgroups')
        students=self.selenium.find_elements_by_css_selector('.groupInfoWrapper')
        self.assertEquals(len(students), 8)

    #def test_listcontent(self):

