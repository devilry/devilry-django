from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase

class TestCreateNewAssignment(SeleniumTestCase):
    appname = 'themebase'
    def test_jasmine(self):
        self.runJasmineTests()
