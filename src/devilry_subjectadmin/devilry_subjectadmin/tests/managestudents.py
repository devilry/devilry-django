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

    def _setupStudentsFull(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1).dl:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student2):examiner(examiner1).dl:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g3:candidate(student3):examiner(examiner1).dl:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g4:candidate(student4):examiner(examiner1).dl:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g5:candidate(student5):examiner(examiner2).dl:ends(5)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g6:candidate(student6):examiner(examiner2).dl:ends(5)')
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
        self.setUpStudentsBasic()
        self._browseToManagestudentsAs('a1admin', self.testhelper.sub_p1_a1)
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsoverview', timeout=20)

        self.waitForCssSelector('.devilry_subjectadmin_listofgroups')
        self.waitForCssSelector('.groupInfoWrapper')
        students=self.selenium.find_elements_by_css_selector('.groupInfoWrapper')
        self.assertEquals(len(students), 3)

    def test_listcontent(self):
        self._setupStudentsFull()
        self._browseToManagestudentsAs('a1admin', self.testhelper.sub_p1_a1)
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsoverview', timeout=20)

        self.waitForCssSelector('.devilry_subjectadmin_listofgroups')
        self.waitForCssSelector('.groupInfoWrapper')

        ident=self.selenium.find_elements_by_css_selector('.groupInfoWrapper')
        self.assertIn('student1', ident[0].text)
        self.assertIn('student7', ident[6].text)
        self.assertIn('Passed (A)', ident[0].text)
        self.assertIn('Failed (F)', ident[4].text)

        stat=self.selenium.find_elements_by_css_selector('.metadataWrapper')
        self.assertIn('Closed', stat[0].text)
        self.assertIn('3 Deliveries', stat[0].text)

        self.assertIn('Open', stat[6].text)

    def _clickButton(self, parent, buttoncls):
        button = parent.find_element_by_css_selector('.{0} button'.format(buttoncls))
        button.click()

    def _clickLink(self, parent, buttoncls):
        button = parent.find_element_by_css_selector('.{0} a'.format(buttoncls))
        button.click()

    def _get_number_of_selected(self, rootbutton, rootmenu, subbutton, submenu, selection, select_menu=None):
        self._setupStudentsFull()
        self._browseToManagestudentsAs('a1admin', self.testhelper.sub_p1_a1)
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsoverview', timeout=20)

        self.waitForCssSelector('.devilry_subjectadmin_listofgroups')
        self.waitForCssSelector('.groupInfoWrapper')
        self._clickButton(self.selenium, rootbutton)

        self.waitForCssSelector('.{0}'.format(rootmenu))
        menu = self.selenium.find_element_by_css_selector('.{0}'.format(rootmenu))

        self.waitForCssSelector('.{0}'.format(subbutton))
        self._clickLink(menu, subbutton)

        self.waitForCssSelector('.{0}'.format(submenu))
        submenu = self.selenium.find_element_by_css_selector('.{0}'.format(submenu))

        self.waitForCssSelector('.{0}'.format(selection))
        self._clickLink(submenu, selection)

        if not select_menu == None:
            self.waitForCssSelector('.{0}'.format(select_menu[0]))
            specificmenu=self.selenium.find_element_by_css_selector('.{0}'.format(select_menu[0]))
            elements=specificmenu.find_elements_by_css_selector('.x-menu-item')

            elements[select_menu[1]].click()


        selected=self.selenium.find_elements_by_css_selector('.x-grid-row-selected')

        return len(selected)


    def test_select_by_status(self):
        count=self._get_number_of_selected('selectButton',
                                           'replaceSelectionMenu',
                                           'byStatusButton',
                                           'byStatusMenu',
                                           'selectStatusOpen')

        self.assertEquals(count, 4)

    def test_select_by_feedback(self):
        count=self._get_number_of_selected('selectButton',
                                           'replaceSelectionMenu',
                                           'byFeedbackButton',
                                           'byFeedbackMenu',
                                           'selectGradePassed')

        self.assertEquals(count, 3)

    def test_select_by_deliveries(self):
        count=self._get_number_of_selected('selectButton',
                                           'replaceSelectionMenu',
                                           'byDeliveryNumButton',
                                           'byDeliveryMenu',
                                           'selectHasDeliveries')

        self.assertEquals(count, 6)

    def test_select_by_examiner(self):
        count=self._get_number_of_selected('selectButton',
                                           'replaceSelectionMenu',
                                           'byExaminerButton',
                                           'byExaminerMenu',
                                           'selectNoExaminer')

        self.assertEquals(count, 2)

    def test_select_by_tag(self):
        count=self._get_number_of_selected('selectButton',
                                           'replaceSelectionMenu',
                                           'byTagButton',
                                           'byTagMenu',
                                           'selectNoTag')

        self.assertEquals(count, 8)

    def test_select_by_specific_examiner(self):
        count=self._get_number_of_selected('selectButton',
                                           'replaceSelectionMenu',
                                           'byExaminerButton',
                                           'byExaminerMenu',
                                           'selectBySpecificExaminer',
                                           ['devilry_subjectadmin_dynamicloadmenu', 0])

        self.assertEquals(count, 4)

    def test_select_by_specific_num_delivery(self):
        count=self._get_number_of_selected('selectButton',
                                           'replaceSelectionMenu',
                                           'byDeliveryNumButton',
                                           'byDeliveryMenu',
                                           'selectByDeliveryExactNum',
                                           ['devilry_subjectadmin_dynamicloadmenu', 0])

        self.assertEquals(count, 2)

    def test_select_by_specific_feedback_grade(self):
        count=self._get_number_of_selected('selectButton',
                                           'replaceSelectionMenu',
                                           'byFeedbackButton',
                                           'byFeedbackMenu',
                                           'selectByFeedbackWithGrade',
                                           ['devilry_subjectadmin_dynamicloadmenu', 0])

        self.assertEquals(count, 1)

    def test_select_by_specific_feedback_points(self):
        count=self._get_number_of_selected('selectButton',
                                           'replaceSelectionMenu',
                                           'byFeedbackButton',
                                           'byFeedbackMenu',
                                           'selectByFeedbackWithPoints',
                                           ['devilry_subjectadmin_dynamicloadmenu', 0])

        self.assertEquals(count, 1)
