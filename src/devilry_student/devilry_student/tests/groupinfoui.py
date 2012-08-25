#from devilry.apps.core.models import 
from datetime import datetime, timedelta
from devilry.apps.core.testhelper import TestHelper

from .base import StudentSeleniumTestCase


class TestGroupInfoUI(StudentSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_user('student1')
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-3):ends(10)'],
                            assignments=['a1:pub(1):ln(Assignment One)'])
        self.fileinfo = {'ok.py': ['print ', 'meh']}

    def _browseToGroup(self, groupid):
        self.browseTo('/group/{groupid}/'.format(groupid=groupid))

    #def _browseToDelivery(self, groupid, deliveryid):
        #self.browseTo('/group/{groupid}/{deliveryid}'.format(groupid=groupid,
                                                             #deliveryid=deliveryid))

    def _browseToAddDelivery(self, groupid, deliveryid):
        self.browseTo('/group/{groupid}/@@add-delivery'.format(groupid=groupid))

    def test_doesnotexists(self):
        self.login('student1')
        self._browseToGroup(100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessage')
        self.assertTrue('Permission denied' in self.selenium.page_source)

    def test_info(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.login('student1')
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')

        # Header
        self.assertTrue('Assignment One' in self.selenium.page_source)
        self.assertTrue('sub.p1.a1' in self.selenium.page_source)

        # Group info
        self.assertEquals(self.selenium.find_element_by_css_selector('.groupnameblock h3').text.strip(), 'Group name')
        self.assertEquals(self.selenium.find_element_by_css_selector('.groupnameblock .groupname').text.strip(), 'g1')
        self.assertEquals(self.selenium.find_element_by_css_selector('.candidatesblock').text.strip(), '')
        self.assertEquals(self.selenium.find_element_by_css_selector('.examinersblock h3').text.strip(), 'Examiner')
        self.assertEquals(self.selenium.find_element_by_css_selector('.examinersblock small').text.strip(), 'No examiner')
        self.assertEquals(self.selenium.find_element_by_css_selector('.gradeblock h3').text.strip(), 'Grade')
        self.assertEquals(self.selenium.find_element_by_css_selector('.gradeblock small').text.strip(), 'No feedback')
        self.assertEquals(self.selenium.find_element_by_css_selector('.statusblock h3').text.strip(), 'Status')
        self.assertEquals(self.selenium.find_element_by_css_selector('.statusblock .label-success').text.strip(), 'Open')
        self.assertEquals(len(self.selenium.find_elements_by_css_selector('.deliveriesblock li')), 0)
        self.assertEquals(self.selenium.find_element_by_css_selector('.adddeliveryblock').text.strip(), '')

    def test_no_groupname(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.login('student1')
        self.testhelper.sub_p1_a1_g1.name = ''
        self.testhelper.sub_p1_a1_g1.save()
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')
        self.assertEquals(self.selenium.find_element_by_css_selector('.groupnameblock').text.strip(), '')

    def test_userlists(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1,student2):examiner(examiner1,examiner2)')
        self.testhelper.student1.devilryuserprofile.full_name = 'Student One'
        self.testhelper.student1.devilryuserprofile.save()
        self.login('student1')
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')

        self.assertEquals(self.selenium.find_element_by_css_selector('.candidatesblock h3').text.strip(), 'Students')
        candidatelinks = self.selenium.find_elements_by_css_selector('.candidatesblock li a')
        self.assertEquals(len(candidatelinks), 2)
        names = map(lambda c: c.text.strip(), candidatelinks)
        self.assertEquals(set(names), set(['Student One', 'student2']))

        self.assertEquals(self.selenium.find_element_by_css_selector('.examinersblock h3').text.strip(), 'Examiners')
        examinerlinks = self.selenium.find_elements_by_css_selector('.examinersblock li a')
        self.assertEquals(len(examinerlinks), 2)
        names = map(lambda c: c.text.strip(), examinerlinks)
        self.assertEquals(set(names), set(['examiner1', 'examiner2']))

    def test_anonymous(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.sub_p1_a1.anonymous = True
        self.testhelper.sub_p1_a1.save()
        self.login('student1')
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')
        self.assertEquals(self.selenium.find_element_by_css_selector('.examinersblock').text.strip(), '')

    def test_hard_deadline_expired(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1:ends(1)')
        self.testhelper.sub_p1_a1.deadline_handling = 1 # Hard deadlines
        self.testhelper.sub_p1_a1.save()
        self.login('student1')
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')
        self.assertEquals(self.selenium.find_element_by_css_selector('.statusblock h3').text.strip(), 'Status')
        self.assertEquals(self.selenium.find_element_by_css_selector('.statusblock .label-important').text.strip(), 'Deadline expired')
        self.assertEquals(self.selenium.find_element_by_css_selector('.adddeliveryblock').text.strip(), '')

    def test_hard_deadline_not_expired(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1:ends(1)')
        self.testhelper.sub_p1_a1.deadline_handling = 1 # Hard deadlines
        self.testhelper.sub_p1_a1.save()
        deadline = self.testhelper.sub_p1_a1_g1_d1
        deadline.deadline = datetime.now() + timedelta(days=2)
        deadline.save()
        self.login('student1')
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')
        self.assertEquals(self.selenium.find_element_by_css_selector('.statusblock h3').text.strip(), 'Status')
        self.assertEquals(self.selenium.find_element_by_css_selector('.statusblock .label-success').text.strip(), 'Open')
        self.assertEquals(self.selenium.find_element_by_css_selector('.adddeliveryblock .add_delivery_link').text.strip(), 'Add delivery')

    def _expand_deadline(self, deadline):
        clickable = self.selenium.find_element_by_css_selector('#deadlinepanel-{0} .x-panel-header'.format(deadline.id))
        clickable.click()
        self.waitForCssSelector('#deadlinepanel-{0} .x-panel-body'.format(deadline.id))
        return self.selenium.find_element_by_css_selector('#deadlinepanel-{0}'.format(deadline.id))

    def test_no_feedback(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1')
        delivery = self.testhelper.add_delivery('sub.p1.a1.g1', self.fileinfo)
        self.login('student1')
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')
        self.assertEquals(self.selenium.find_element_by_css_selector('.gradeblock small').text.strip(), 'No feedback')
        self.assertEquals(self.selenium.find_element_by_css_selector('.statusblock .label-success').text.strip(), 'Open')
        self.assertEquals(len(self.selenium.find_elements_by_css_selector('.deliveriesblock li')), 1)

        deadlinepanel = self._expand_deadline(self.testhelper.sub_p1_a1_g1_d1)
        deliverypanel = deadlinepanel.find_elements_by_css_selector('.devilry_student_groupinfo_delivery')[0]
        self.assertEquals(deliverypanel.find_element_by_css_selector('.gradeblock').text.strip(), '')
        self.assertEquals(deliverypanel.find_element_by_css_selector('.rendered_view small').text.strip(), 'No feedback')

    def test_passing_grade(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1')
        delivery = self.testhelper.add_delivery('sub.p1.a1.g1', self.fileinfo)
        self.testhelper.add_feedback(delivery, verdict={'grade': 'A', 'points': 10, 'is_passing_grade': True},
                                     rendered_view='Good stuff')
        self.login('student1')
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')
        self.assertEquals(self.selenium.find_element_by_css_selector('.gradeblock .success').text.strip(), 'Passed')
        self.assertEquals(self.selenium.find_element_by_css_selector('.gradeblock small').text.strip(), '(A)')
        self.assertEquals(self.selenium.find_element_by_css_selector('.statusblock .label-warning').text.strip(), 'Closed')
        self.assertEquals(len(self.selenium.find_elements_by_css_selector('.deliveriesblock li')), 1)

        deadlinepanel = self._expand_deadline(self.testhelper.sub_p1_a1_g1_d1)
        deliverypanel = deadlinepanel.find_elements_by_css_selector('.devilry_student_groupinfo_delivery')[0]
        self.assertEquals(deliverypanel.find_element_by_css_selector('.gradeblock h4').text.strip(), 'Grade')
        self.assertEquals(deliverypanel.find_element_by_css_selector('.gradeblock .success').text.strip(), 'Passed')
        self.assertEquals(deliverypanel.find_element_by_css_selector('.gradeblock small').text.strip(), '(A)')
        self.assertEquals(deliverypanel.find_element_by_css_selector('.rendered_view').text.strip(), 'Good stuff')

    def test_failing_grade(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1')
        delivery = self.testhelper.add_delivery('sub.p1.a1.g1', self.fileinfo)
        self.testhelper.add_feedback(delivery, verdict={'grade': 'F', 'points': 2, 'is_passing_grade': False},
                                     rendered_view='Bad stuff')
        self.login('student1')
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')
        self.assertEquals(self.selenium.find_element_by_css_selector('.gradeblock .danger').text.strip(), 'Failed')
        self.assertEquals(self.selenium.find_element_by_css_selector('.gradeblock small').text.strip(), '(F)')
        self.assertEquals(self.selenium.find_element_by_css_selector('.statusblock .label-warning').text.strip(), 'Closed')
        self.assertEquals(len(self.selenium.find_elements_by_css_selector('.deliveriesblock li')), 1)

        deadlinepanel = self._expand_deadline(self.testhelper.sub_p1_a1_g1_d1)
        deliverypanel = deadlinepanel.find_elements_by_css_selector('.devilry_student_groupinfo_delivery')[0]
        self.assertEquals(deliverypanel.find_element_by_css_selector('.gradeblock h4').text.strip(), 'Grade')
        self.assertEquals(deliverypanel.find_element_by_css_selector('.gradeblock .danger').text.strip(), 'Failed')
        self.assertEquals(deliverypanel.find_element_by_css_selector('.gradeblock small').text.strip(), '(F)')
        self.assertEquals(deliverypanel.find_element_by_css_selector('.rendered_view').text.strip(), 'Bad stuff')

    def test_deliverieslist(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1')
        self.testhelper.add_delivery('sub.p1.a1.g1', self.fileinfo)
        self.testhelper.add_delivery('sub.p1.a1.g1', self.fileinfo)
        self.testhelper.add_delivery('sub.p1.a1.g1', self.fileinfo)
        self.login('student1')
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')
        self.assertEquals(len(self.selenium.find_elements_by_css_selector('.deliveriesblock li')), 3)

    def test_deadlinetext(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1')
        deadline = self.testhelper.sub_p1_a1_g1_d1
        deadline.text = 'This is a test'
        deadline.save()
        self.login('student1')
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')
        deadlinepanel = self._expand_deadline(self.testhelper.sub_p1_a1_g1_d1)
        self.assertEquals(deadlinepanel.find_element_by_css_selector('.deadlinetext h2').text.strip(),
                          'About this deadline')
        deadlinetextpara = deadlinepanel.find_element_by_css_selector('.deadlinetext p')
        self.assertEquals(deadlinetextpara.text.strip(), 'This is a test')
        self.assertEquals(deadlinetextpara.get_attribute('style').strip(), 'white-space: pre-wrap;')

    def test_no_deadlinetext(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1')
        self.login('student1')
        self._browseToGroup(self.testhelper.sub_p1_a1_g1.id)
        self.waitForCssSelector('.devilry_student_groupmetadata')
        deadlinepanel = self._expand_deadline(self.testhelper.sub_p1_a1_g1_d1)
        self.assertEquals(deadlinepanel.find_element_by_css_selector('.deadlinetext').text.strip(), '')

    #def test_add_delivery(self):
        #self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        #self.login('student1')
        #self._browseToAddDelivery(self.testhelper.sub_p1_a1_g1.id)
        #self.waitForCssSelector('.devilry_student_groupmetadata')
