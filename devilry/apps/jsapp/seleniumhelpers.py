from selenium.webdriver.support.ui import WebDriverWait
from unittest import TestCase
from selenium import webdriver


class SeleniumMixin(object):
    def getDriver(self):
        return getattr(webdriver, self.seleniumbrowser)()

    def getJsBaseUrl(self, appname):
        return 'http://localhost:8000/{0}'.format(appname)

    def getJsAppTestUrl(self, appname):
        return '{0}/test'.format(self.getJsBaseUrl(appname))

    def getJsAppJasmineTestUrl(self, appname):
        return '{0}/jasminetest'.format(self.getJsBaseUrl(appname))

    def getHashUrl(self, appname, path):
        return '{0}#{1}'.format(self.getJsAppTestUrl(appname), path)

    def driverWaitForCssSelector(self, driver, cssselector, timeout=10):
        WebDriverWait(driver, timeout).until(lambda driver: driver.find_elements_by_css_selector(cssselector))

    def driverWaitForEnabled(self, driver, element, timeout=10):
        WebDriverWait(driver, timeout).until(lambda driver: element.is_enabled())


class SeleniumTestCase(TestCase, SeleniumMixin):
    appname = None

    def setUp(self):
        self.driver = self.getDriver()

    def tearDown(self):
        self.driver.close()

    def waitForCssSelector(self, cssselector, timeout=10):
        return self.driverWaitForCssSelector(self.driver, cssselector, timeout)

    def waitForEnabled(self, element, timeout=10):
        return self.driverWaitForEnabled(self.driver, element, timeout)

    def browseToTest(self, path):
        self.driver.get(self.getHashUrl(self.appname, path))

    def browseToJasmine(self):
        self.driver.get(self.getJsAppJasmineTestUrl(self.appname))

    def runJasmineTests(self, ):
        self.browseToJasmine()
        self.waitForCssSelector('.jasmine_reporter')
        self.assertTrue('0 failures' in self.driver.page_source)
