from datetime import datetime
from devilry.apps.core.testhelper import TestHelper
from .base import StudentSeleniumTestCase


def ui_datetimeformat(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M:%S')

class TestDashboardUI(StudentSeleniumTestCase):
    def setUp(self):
        self.fileinfo = {'ok.py': ['print ', 'meh']}
        self.testhelper = TestHelper()
        self.testhelper.create_user('student1')
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-3):ends(10)'], # -3months
                            assignments=['a1:pub(1)', # 1 days after p1 begins
                                         'a2:pub(30)']) # 30days after p1 begins

    def _browseToDashboard(self):
        self.browseTo('')

    def test_not_student(self):
        self.login('student1')
        self._browseToDashboard()
        self.waitForCssSelector('.devilry_student_dashboard')
        self.assertTrue('You have no active electronic assignments' in self.selenium.page_source)
        self.assertTrue('Other assignments' in self.selenium.page_source)
        self.assertTrue('Browse all your assignments' in self.selenium.page_source)
        self.assertTrue('Search your assignments' in self.selenium.page_source)

    #
    #
    # Not expired deadlines
    #
    #

    def test_open_before_deadline(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(110)') # 110 days after a1 published
        deadline1 = self.testhelper.sub_p1_a1_g1_d1

        self.login('student1')
        self._browseToDashboard()
        self.waitForCssSelector('.devilry_student_dashboard')
        self.waitForCssSelector('.devilry_student_opengroupsgrid.not_expired')
        grid = self.selenium.find_element_by_css_selector('.devilry_student_opengroupsgrid.not_expired')
        rows = grid.find_elements_by_css_selector('.x-grid-row')
        self.assertEquals(len(rows), 1)
        row0 = rows[0]
        self.assertEquals(row0.find_element_by_css_selector('.ident').text.strip(), 'sub - A1')
        self.assertEquals(row0.find_element_by_css_selector('.deliveries').text.strip(), 'Deliveries: 0')
        self.assertEquals(len(row0.find_elements_by_css_selector('.deadlinedelta.success')), 1)
        self.assertEquals(len(row0.find_elements_by_css_selector('.deadlinedelta.danger')), 0)
        self.assertEquals(row0.find_element_by_css_selector('.deadline').text.strip(),
                          'Deadline: {0}'.format(ui_datetimeformat(deadline1.deadline)))

    def test_multiple_open_before_deadline(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(110)') # 110 days after a1 published
        self.testhelper.add_to_path('uni;sub.p1.a2.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a2.g1.d1:ends(100)') # 100 days after a2 published

        self.login('student1')
        self._browseToDashboard()
        self.waitForCssSelector('.devilry_student_dashboard')
        self.waitForCssSelector('.devilry_student_opengroupsgrid.not_expired')
        grid = self.selenium.find_element_by_css_selector('.devilry_student_opengroupsgrid.not_expired')
        rows = grid.find_elements_by_css_selector('.x-grid-row')
        self.assertEquals(len(rows), 2)
        self.assertEquals(rows[0].find_element_by_css_selector('.ident').text.strip(), 'sub - A1')
        self.assertEquals(rows[1].find_element_by_css_selector('.ident').text.strip(), 'sub - A2')

    def test_open_before_deadline_deliveries(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(110)') # 110 days after a1 published
        for x in xrange(3):
            self.testhelper.add_delivery('sub.p1.a1.g1', self.fileinfo)

        self.login('student1')
        self._browseToDashboard()
        self.waitForCssSelector('.devilry_student_dashboard')
        self.waitForCssSelector('.devilry_student_opengroupsgrid.not_expired')
        grid = self.selenium.find_element_by_css_selector('.devilry_student_opengroupsgrid.not_expired')
        rows = grid.find_elements_by_css_selector('.x-grid-row')
        self.assertEquals(len(rows), 1)
        self.assertEquals(rows[0].find_element_by_css_selector('.ident').text.strip(), 'sub - A1')
        self.assertEquals(rows[0].find_element_by_css_selector('.deliveries').text.strip(), 'Deliveries: 3')



    #
    #
    # Expired deadlines
    #
    #

    def test_open_deadline_expired(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(20)') # 20 days after a1 published (which is in the past)
        deadline1 = self.testhelper.sub_p1_a1_g1_d1

        self.login('student1')
        self._browseToDashboard()
        self.waitForCssSelector('.devilry_student_dashboard')
        self.waitForCssSelector('.devilry_student_opengroupsgrid.expired')
        grid = self.selenium.find_element_by_css_selector('.devilry_student_opengroupsgrid.expired')
        rows = grid.find_elements_by_css_selector('.x-grid-row')
        self.assertEquals(len(rows), 1)
        row0 = rows[0]
        self.assertEquals(row0.find_element_by_css_selector('.ident').text.strip(), 'sub - A1')
        self.assertEquals(row0.find_element_by_css_selector('.deliveries').text.strip(), 'Deliveries: 0')
        self.assertEquals(len(row0.find_elements_by_css_selector('.deadlinedelta.success')), 0)
        self.assertEquals(len(row0.find_elements_by_css_selector('.deadlinedelta.danger')), 1)
        self.assertEquals(row0.find_element_by_css_selector('.deadline').text.strip(),
                          'Deadline: {0}'.format(ui_datetimeformat(deadline1.deadline)))
        self.assertTrue('You have no active electronic assignments' in self.selenium.page_source)

    def test_multiple_open_deadline_expired(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(20)') # 110 days after a1 published
        self.testhelper.add_to_path('uni;sub.p1.a2.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a2.g1.d1:ends(30)') # 100 days after a2 published

        self.login('student1')
        self._browseToDashboard()
        self.waitForCssSelector('.devilry_student_dashboard')
        self.waitForCssSelector('.devilry_student_opengroupsgrid.expired')
        grid = self.selenium.find_element_by_css_selector('.devilry_student_opengroupsgrid.expired')
        rows = grid.find_elements_by_css_selector('.x-grid-row')
        self.assertEquals(len(rows), 2)
        self.assertEquals(rows[0].find_element_by_css_selector('.ident').text.strip(), 'sub - A1')
        self.assertEquals(rows[1].find_element_by_css_selector('.ident').text.strip(), 'sub - A2')

    def test_open_deadline_expired_deliveries(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(20)') # 20 days after a1 published (which is in the past)
        for x in xrange(3):
            self.testhelper.add_delivery('sub.p1.a1.g1', self.fileinfo)

        self.login('student1')
        self._browseToDashboard()
        self.waitForCssSelector('.devilry_student_dashboard')
        self.waitForCssSelector('.devilry_student_opengroupsgrid.expired')
        grid = self.selenium.find_element_by_css_selector('.devilry_student_opengroupsgrid.expired')
        rows = grid.find_elements_by_css_selector('.x-grid-row')
        self.assertEquals(len(rows), 1)
        self.assertEquals(rows[0].find_element_by_css_selector('.ident').text.strip(), 'sub - A1')
        self.assertEquals(rows[0].find_element_by_css_selector('.deliveries').text.strip(), 'Deliveries: 3')


    #
    #
    # Hard deadlines
    #
    #
    def test_hard_deadlines(self):
        # Test that hard deadlines actually show up before they expire, but not after
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(10)') # 10 days after a1 published (in the past)
        self.testhelper.add_to_path('uni;sub.p1.a2.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a2.g1.d1:ends(110)') # 110 days after a1 published (in the future)
        self.assertTrue(self.testhelper.sub_p1_a1_g1_d1.deadline < datetime.now())
        self.assertTrue(self.testhelper.sub_p1_a2_g1_d1.deadline > datetime.now())

        # Hard deadlines
        for assignment in (self.testhelper.sub_p1_a1, self.testhelper.sub_p1_a2):
            assignment.deadline_handling = 1
            assignment.save()

        self.login('student1')
        self._browseToDashboard()
        self.waitForCssSelector('.devilry_student_dashboard')
        self.waitForCssSelector('.devilry_student_opengroupsgrid.not_expired')
        grid = self.selenium.find_element_by_css_selector('.devilry_student_opengroupsgrid.not_expired')
        rows = grid.find_elements_by_css_selector('.x-grid-row')
        self.assertEquals(len(rows), 1)
        self.assertEquals(rows[0].find_element_by_css_selector('.ident').text.strip(), 'sub - A2')

        # Make sure A1 does not end up in the expired SOFT deadlines grid
        expiredgrid = self.selenium.find_element_by_css_selector('.devilry_student_opengroupsgrid.expired')
        expiredrows = expiredgrid.find_elements_by_css_selector('.x-grid-row')
        self.assertEquals(len(expiredrows), 0)


    #
    #
    # Recent deliveries
    #
    #

    def test_recent_deliveries(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(110)') # 110 days after a1 published
        for x in xrange(3):
            self.testhelper.add_delivery('sub.p1.a1.g1', self.fileinfo, time_of_delivery=x)

        self.login('student1')
        self._browseToDashboard()
        self.waitForCssSelector('.devilry_student_dashboard')
        self.waitForCssSelector('.devilry_student_recentdeliveriesgrid')
        grid = self.selenium.find_element_by_css_selector('.devilry_student_recentdeliveriesgrid')
        rows = grid.find_elements_by_css_selector('.x-grid-row')
        self.assertEquals(len(rows), 3)
        self.assertEquals(rows[0].find_element_by_css_selector('.ident').text.strip(), 'sub - a1 - #3')
        self.assertEquals(rows[1].find_element_by_css_selector('.ident').text.strip(), 'sub - a1 - #2')
        self.assertEquals(rows[2].find_element_by_css_selector('.ident').text.strip(), 'sub - a1 - #1')

    def test_recent_feedbacks(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(110)') # 110 days after a1 published

        # Add 2 deliveries, delivery1 has 2 feedbacks, and delivery2 has 1 feedback.
        delivery1 = self.testhelper.add_delivery('sub.p1.a1.g1', self.fileinfo)
        self.testhelper.add_feedback(delivery1,
                                     verdict={'grade': 'A', 'points': 10, 'is_passing_grade': True})
        delivery1feedback = self.testhelper.add_feedback(delivery1,
                                                 verdict={'grade': 'F', 'points': 2, 'is_passing_grade': False})
        delivery2 = self.testhelper.add_delivery('sub.p1.a1.g1', self.fileinfo)
        delivery2feedback = self.testhelper.add_feedback(delivery2,
                                                 verdict={'grade': 'C', 'points': 5, 'is_passing_grade': True})

        self.login('student1')
        self._browseToDashboard()
        self.waitForCssSelector('.devilry_student_dashboard')
        self.waitForCssSelector('.devilry_student_recentfeedbacksgrid')
        grid = self.selenium.find_element_by_css_selector('.devilry_student_recentfeedbacksgrid')
        rows = grid.find_elements_by_css_selector('.x-grid-row')
        self.assertEquals(len(rows), 2) # Notice that only 2 is included - because only active feedbacks are included
        self.assertEquals(rows[0].find_element_by_css_selector('.ident').text.strip(), 'sub - a1 - #2')
        self.assertEquals(rows[0].find_element_by_css_selector('.passing_grade.success').text.strip(), 'Passed')
        self.assertEquals(rows[0].find_element_by_css_selector('.grade').text.strip(), '(C)')
        self.assertEquals(rows[1].find_element_by_css_selector('.ident').text.strip(), 'sub - a1 - #1')
        self.assertEquals(rows[1].find_element_by_css_selector('.failing_grade.danger').text.strip(), 'Failed')
        self.assertEquals(rows[1].find_element_by_css_selector('.grade').text.strip(), '(F)')
