from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase


class TestDashboard(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_superuser('grandma')
        self.login('grandma')

        self.testhelper.add(nodes='uni',
                            subjects=['duck1100', 'duck1010:ln(DUCK 1010 - Programming)'],
                            periods=['2012h:begins(-1)'],
                            assignments=['week1:ln(Week One)', 'week2', 'week3', 'week4'])
        self.testhelper.add(nodes='uni',
                            subjects=['duck1010'],
                            periods=['oldperiod:begins(-100)'],
                            assignments=['oldassignment'])

    def test_dashboard(self):
        self.browseTo('')
        self.waitForCssSelector('.shortcutlist')
        self.assertTrue('Active subjects' in self.selenium.page_source)
        self.assertFalse('oldperiod' in self.selenium.page_source)
        self.assertFalse('oldassignment' in self.selenium.page_source)
        self.assertEquals(self.selenium.page_source.count('Week One'), 2)
        self.assertEquals(self.selenium.page_source.count('Add assignment'), 2)
        self.assertTrue('duck1010' in self.selenium.page_source)
        self.assertEquals(len(self.selenium.find_elements_by_link_text('Add assignment')), 2)
        self.assertEquals(len(self.selenium.find_elements_by_link_text('Week One')), 2)

        browse_all_buttons = self.selenium.find_elements_by_link_text('Browse all your subjects (including old/archived)')
        self.assertEquals(len(browse_all_buttons), 1)
        self.assertEquals(browse_all_buttons[0].get_attribute('href'),
                          self.get_absolute_url('/'))
