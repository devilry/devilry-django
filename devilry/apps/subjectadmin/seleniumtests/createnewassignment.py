from devilry.apps.guibase.seleniumhelpers import SeleniumTestCase


class TestCreateNewAssignment(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_chooseperiod_render(self):
        self.browseTo('/@@create-new-assignment/@@chooseperiod')
        self.waitForCssSelector('.activeperiodslist')
        self.assertTrue('duck-mek2030.2012h' in self.driver.page_source)
        self.assertTrue('duck1100.2011h' in self.driver.page_source)
        self.assertTrue('subjectadmin.chooseperiod.title' in self.driver.page_source)
        self.assertTrue('subjectadmin.chooseperiod.sidebarhelp' in self.driver.page_source)
        self.assertTrue('subjectadmin.next' in self.driver.page_source)
        periodlist = self.driver.find_element_by_class_name('activeperiodslist')
        self.assertEquals(len(periodlist.find_elements_by_css_selector('tr.x-grid-row')), 3)

    def test_chooseperiod_nextbutton(self):
        self.browseTo('/@@create-new-assignment/@@chooseperiod')
        self.waitForCssSelector('.nextbutton')
        nextbutton = self.driver.find_element_by_class_name('nextbutton')
        buttonel = nextbutton.find_element_by_tag_name('button')
        self.assertFalse(buttonel.is_enabled())

        # Click first element in the periodlist and make sure nextbutton is enabled afterwards
        periodlist = self.driver.find_element_by_class_name('activeperiodslist')
        firstperiod = periodlist.find_elements_by_css_selector('tr.x-grid-row')[0]
        firstperiod.click()
        self.assertTrue(buttonel.is_enabled())
