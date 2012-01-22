from unittest import TestCase
from selenium import webdriver


class SeleniumMixin(object):
    def getBrowser(self):
        return getattr(webdriver, self.seleniumbrowser)()

    def getJsAppUrl(self, urlprefix):
        return 'http://localhost:8000/{0}/test'.format(urlprefix)


class SeleniumTestCase(TestCase, SeleniumMixin):
    appname = None

    def setUp(self):
        self.browser = self.getBrowser()
        self.browser.get(self.getJsAppUrl(self.appname))

    def tearDown(self):
        self.browser.close()
