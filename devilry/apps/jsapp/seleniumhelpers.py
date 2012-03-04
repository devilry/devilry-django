import json
from selenium.webdriver.support.ui import WebDriverWait
from unittest import TestCase, skipIf
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from django.conf import settings


class SeleniumMixin(object):
    def getDriver(self):
        return getattr(webdriver, settings.SELENIUM_BROWSER)()

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

    def driverWaitForText(self, driver, text, timeout=10):
        WebDriverWait(driver, timeout).until(lambda driver: text in driver.page_source)

@skipIf(hasattr(settings, 'SKIP_SELENIUMTESTS') and settings.SKIP_SELENIUMTESTS,
    'Selenium tests have been disabled in settings.py using SKIP_SELENIUMTESTS=True.')
class SeleniumTestCase(TestCase, SeleniumMixin):
    appname = None

    def setUp(self):
        self.driver = self.getDriver()
        self.afterSetUp()

    def afterSetUp(self):
        """
        Override this instead of ``setUp()``.
        """

    def tearDown(self):
        self.driver.close()

    def waitForCssSelector(self, cssselector, timeout=10):
        return self.driverWaitForCssSelector(self.driver, cssselector, timeout)

    def waitForEnabled(self, element, timeout=10):
        return self.driverWaitForEnabled(self.driver, element, timeout)

    def waitForText(self, text, timeout=10):
        return self.driverWaitForText(self.driver, text, timeout)

    def browseToTest(self, path):
        self.driver.get(self.getHashUrl(self.appname, path))

    def browseToJasmine(self):
        self.driver.get(self.getJsAppJasmineTestUrl(self.appname))

    def runJasmineTests(self):
        self.browseToJasmine()
        self.waitForCssSelector('.jasmine_reporter')
        self.assertTrue('0 failures' in self.driver.page_source)

    def executeScript(self, script, element):
        return self.driver.execute_script(script, element)

    def getInnerHtml(self, element):
        return self.executeScript("return arguments[0].innerHTML", element)

    def getHiddenElementProxyDecoded(self, proxyid):
        return json.loads(self.getHiddenElementProxyRawtext(proxyid))

    def getHiddenElementProxyRawtext(self, proxyid):
        css_selector = '#{0} .hiddenelement-text'.format(proxyid)
        self.waitForCssSelector(css_selector)
        proxyelement = self.driver.find_element_by_css_selector(css_selector)
        self.waitFor(proxyelement, lambda element: len(self.getInnerHtml(element)) > 0)
        return self.getInnerHtml(proxyelement)

    def waitFor(self, item, fn, timeout=10):
        """
        Wait for the ``fn`` function to return ``True``. The ``item`` is
        forwarded as argument to ``fn``.

        Example (wait for text in an element)::

            waitFor(myelem, lambda myelem: len(myelem.text) > 0)
        """
        WebDriverWait(item, timeout).until(fn)

    def failIfCssSelectorNotFound(self, element, css_selector):
        """
        Assert that ``element.find_element_by_css_selector(css_selector)``
        raises ``NoSuchElementException``.
        """
        with self.assertRaises(NoSuchElementException):
            element.find_element_by_css_selector(css_selector)
