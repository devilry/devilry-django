from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase


class TestDashboard(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_dashboard(self):
        self.browseToTest('')
        self.waitForCssSelector('.shortcutlist')
        self.assertTrue('subjectadmin.dashboard.actionstitle' in self.driver.page_source)
        self.assertTrue('#/@@create-new-assignment/@@chooseperiod' in self.driver.page_source)
        self.assertTrue('href="#/"' in self.driver.page_source)
        #self.assertTrue('#/@@register-for-final-exams' in self.driver.page_source)
        self.assertTrue('#/@@global-statistics' in self.driver.page_source)
        self.assertEquals(len(self.driver.find_elements_by_link_text('subjectadmin.dashboard.createnewassignment')), 1)
        self.assertEquals(len(self.driver.find_elements_by_link_text('subjectadmin.dashboard.browseall')), 1)
        #self.assertEquals(len(self.driver.find_elements_by_link_text('subjectadmin.dashboard.registerqualifiesforfinal')), 1)
        self.assertEquals(len(self.driver.find_elements_by_link_text('subjectadmin.dashboard.overview-and-statistics')), 1)
