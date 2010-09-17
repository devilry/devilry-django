from selenium import selenium
import unittest, time, re

class TestDashboard(unittest.TestCase):
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
    
    def assert403(self, f, *args, **kw):
        try:
            f(*args, **kw)
        except Exception, e:
            self.assertTrue("403" in str(e))
            self.assertTrue("FORBIDDEN" in str(e))
        else:
            self.fail("403 not raised for %s, %s, %s" % (f, args, kw))
    
    def test_normal_workflow(self):
        sel = self.selenium
        try: self.failUnless(sel.is_text_present("Dashboard"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Assignments"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Money making basics"))
        except AssertionError, e: self.verificationErrors.append(str(e))

        sel.click("link=Effective habits for lazy people")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present(
            "tull101.21century.avoiding-work (may)"))
        except AssertionError, e: self.verificationErrors.append(str(e))

        sel.click("//div[@id='content']/table[2]/tbody/tr[4]/td[5]/a")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Still not good enough!"))
        except AssertionError, e: self.verificationErrors.append(str(e))

        sel.click("link=tull101.21century.avoiding-work (may)")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Show feedback")
        sel.wait_for_page_to_load("30000")
        try:
            self.failUnless(sel.is_text_present(
                "Ok i will pass you, but you have to do better on the next assignment."))
        except AssertionError, e: self.verificationErrors.append(str(e))


    def test_forbidden(self):
        sel = self.selenium
        self.assert403(sel.open, "/student/1")
        self.assert403(sel.open, "/student/delivery/1")
        self.assert403(sel.open, "/student/add-delivery/1")
        self.assert403(sel.open, "/student/successful-delivery/1")
        self.assert403(sel.open, "/ui/download-file/3")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
