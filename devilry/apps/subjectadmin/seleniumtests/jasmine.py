from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase

class TestCreateNewAssignment(SeleniumTestCase):
    appname = 'subjectadmin'
    def test_jasmine(self):
        self.runJasmineTests()
