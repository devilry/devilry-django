from devilry.apps.jsapp.seleniumhelpers import SeleniumTestCase


class TestManageStudents(SeleniumTestCase):
    appname = 'subjectadmin'

    def test_doesnotexists(self):
        self.browseToTest('/a/b/c/@@manage-students') # This is not a valid path to an assignment
        self.waitForCssSelector('.managestudentsoverview')
        self.waitForCssSelector('.messagemask')
        self.assertTrue('themebase.doesnotexist' in self.driver.page_source)
        self.assertTrue('a.b.c' in self.driver.page_source)

    def test_load_relatedstudents(self):
        self.browseToTest('/duck1100/2012h/week1/@@manage-students')
        proxytext = self.getHiddenElementProxyRawtext('relatedstudentproxy')
        self.assertTrue('"candidate_id": "secretcand0"' in proxytext)
        self.assertTrue('"candidate_id": "secretcand2"' in proxytext)
        self.assertTrue('"user__devilryuserprofile__full_name": "The Student1",' in proxytext)

    def test_load_relatedexaminers(self):
        self.browseToTest('/duck1100/2012h/week1/@@manage-students')
        proxytext = self.getHiddenElementProxyRawtext('relatedexaminerproxy')
        self.assertTrue('"user__username": "examiner0"' in proxytext)
        self.assertTrue('"user__devilryuserprofile__full_name": "The first examiner",' in proxytext)

    def test_load_groups(self):
        self.browseToTest('/duck1100/2012h/week1/@@manage-students')
        proxytext = self.getHiddenElementProxyRawtext('groupproxy')
        self.assertTrue('"tags": ["group1"],' in proxytext)
        self.assertTrue('"id": 1' in proxytext)
        self.assertTrue('"id": 3' in proxytext)

        # Need the tags to distinguish from proxy data
        self.assertTrue('<strong>The Student0</strong>' in self.driver.page_source)
        self.assertTrue('<small>student2</small>' in self.driver.page_source)
