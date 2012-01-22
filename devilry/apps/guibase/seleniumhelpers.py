from selenium.webdriver.support.ui import WebDriverWait
from unittest import TestCase
from selenium import webdriver


class SeleniumMixin(object):
    def getDriver(self):
        return getattr(webdriver, self.seleniumbrowser)()

    def getJsAppUrl(self, urlprefix):
        return 'http://localhost:8000/{0}/test'.format(urlprefix)

    def driverWaitForCssSelector(self, driver, cssselector, timeout=10):
        WebDriverWait(driver, timeout).until(lambda driver: driver.find_elements_by_css_selector(cssselector))


class SeleniumTestCase(TestCase, SeleniumMixin):
    appname = None

    def setUp(self):
        self.driver = self.getDriver()
        self.driver.get(self.getJsAppUrl(self.appname))

    def tearDown(self):
        self.driver.close()

    def waitForCssSelector(self, cssselector, timeout=10):
        return self.driverWaitForCssSelector(self.driver, cssselector, timeout)
