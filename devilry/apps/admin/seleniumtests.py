from selenium import selenium
import unittest

from devilry.core.testhelpers import SeleniumTestBase


class TestAdminForbidden(SeleniumTestBase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
        sel = self.selenium
        sel.open("/ui/login")
        sel.type("id_username", "may")
        sel.type("id_password", "test")
        sel.click("login")
        sel.wait_for_page_to_load("30000")
    
    def test_forbidden(self):
        """
        Notes:
            - No need to use "forbidden" on the autocoplete-* urls, because
              they only return "where is admin or superadmin".
            - Create node, subject, period and assignment does not need any
              protection because they do not reveal any information at all,
              and the "save" and "edit" views are protected.
        TODO: Test the deletemany views. They require a querystring, and I
                do not know how to handle querystrings in selenium at the
                time of writing.
        """
        sel = self.selenium
        self.assert403(sel.open, "/admin/nodes/1/edit")
        self.assert403(sel.open, "/admin/subjects/1/edit")
        self.assert403(sel.open, "/admin/periods/1/edit")
        self.assert403(sel.open, "/admin/assignments/1/edit")
        self.assert403(sel.open, "/admin/assignments/1/group/edit/9")
        self.assert403(sel.open, "/admin/assignments/1/group/successful-save/9")
        self.assert403(sel.open, "/admin/assignments/1/group/create")
        self.assert403(sel.open, "/admin/assignments/1/create-assignmentgroups")
        self.assert403(sel.open, "/admin/assignments/1/save-assignmentgroups")
        self.assert403(sel.open, "/admin/autocomplete-assignmentgroupname/1")
        self.assert403(sel.open, "/admin/assignments/1/set-examiners")
        self.assert403(sel.open, "/admin/assignments/1/random-dist-examiners")
        self.assert403(sel.open, "/admin/assignments/1/copy-groups")
        self.assert403(sel.open, "/admin/assignments/1/create-deadline")
        self.assert403(sel.open, "/admin/assignments/1/clear-deadlines")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
