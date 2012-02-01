from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase

class TestJasmine(SeleniumTestCase):
    appname = 'themebase'
    def test_jasmine(self):
        self.runJasmineTests()
