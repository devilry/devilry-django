from devilry.apps.guibase.seleniumhelpers import SeleniumTestCase


class TestSelenium(SeleniumTestCase):
    appname = 'subjectadmin'
    def test_list_populated(self):
        self.assertEquals(self.browser.title, 'Devilry')
        #elem = browser.find_element_by_name("p") # Find the query box
        #elem.send_keys("seleniumhq" + Keys.RETURN)
        #time.sleep(0.2) # Let the page load, will be added to the API
        #try:
            #browser.find_element_by_xpath("//a[contains(@href,'http://seleniumhq.org')]")
        #except NoSuchElementException:
            #assert 0, "can't find seleniumhq"
