from selenium import selenium
import unittest

from devilry.core.testhelpers import SeleniumTestBase


class CommonTestsMixin(object):
    def _login(self, username):
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
        sel = self.selenium
        sel.open("/ui/login")
        sel.type("id_username", username)
        sel.type("id_password", "test")
        sel.click("login")
        sel.wait_for_page_to_load("30000")

    def _common(self):
        sel = self.selenium
        sel.open("/examiner/list_assignmentgroups/2")

        self.failUnless(sel.is_text_present("huey, dewey, louie"))
        self.failUnless(sel.is_text_present("Corrected, not published"))

        sel.click("link=Show")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("money101.from2010.money"))
        self.failUnless(sel.is_text_present("Create deadline"))
        self.failUnless(sel.is_text_present("Close group"))
        self.failUnless(sel.is_text_present("2 - 2010-08-05 18:15 ( A ) (Feedback is not published, and not viewable by the student(s))"))
        self.failUnless(sel.is_text_present("1 - 2010-08-05 18:14 ( Not corrected )"))

        sel.click("//div[@id='content']/div[4]/div[3]/h4[1]/a/span")
        sel.click("link=Edit feedback")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("Feedback"))
        self.failUnless(sel.is_element_present("id_grade-grade"))
        self.failUnless(sel.is_element_present("id_feedback-text"))
        self.failUnless(sel.is_element_present("id_feedback-published"))
        self.failUnless(sel.is_text_present("Feedback text"))

        sel.type("id_grade-grade", "B")
        sel.type("id_feedback-text", "This is great work.")
        sel.click("id_feedback-published")
        sel.click("save")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("2 - 2010-08-05 18:15 ( B ) (Published)"))
        self.failUnless(sel.is_text_present("You have published a feedback, but have not given the student(s) a new deadline. You should create a new deadline or close for more deliveries. Closing the group leave the students unable to add more deliveries."))

        sel.click("//a[@id='openclosebtn']/span")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("Assignment group successfully closed."))
        self.failUnless(sel.is_text_present("This group is closed for deliveries. Click 'Open group' to allow students to add new deliveries."))
        sel.click("//a[@id='openclosebtn']/span")
        sel.wait_for_page_to_load("30000")


class TestAsExaminer(SeleniumTestBase, CommonTestsMixin):
    fixtures = ['addons/examiner/fixtures/selenium.json']

    def setUp(self):
        self.load_fixtures()
        self._login("clarabelle")
    
    def test_normal_workflow(self):
        sel = self.selenium
        self.failUnless(sel.is_text_present("Dashboard"))
        self.failUnless(sel.is_text_present("Assignments"))
        self.failUnless(sel.is_text_present("Money making basics"))
        self.failUnless(sel.is_text_present("Tull 101 - The 21 century"))
        self.failUnless(sel.is_text_present("Effective habits for lazy people"))
        self.failUnless(sel.is_text_present("Oblig 1"))

        sel.click("link=Money making basics")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("huey, dewey, louie"))
        self.failUnless(sel.is_text_present("Corrected, not published"))
        self._common()

    def test_forbidden(self):
        sel = self.selenium
        self.assert403(sel.open, "/examiner/show-assignmentgroup/2")
        self.assert403(sel.open, "/examiner/show-assignmentgroup/2")
        self.assert403(sel.open, "/examiner/close-assignmentgroup/2")
        self.assert403(sel.open, "/examiner/correct-delivery/4")
        self.assert403(sel.open, "/examiner/list_assignmentgroups/1")
    
    def tearDown(self):
        self.selenium.stop()


class TestAsSuperadmin(SeleniumTestBase, CommonTestsMixin):
    fixtures = ['addons/examiner/fixtures/selenium.json']

    def setUp(self):
        self.load_fixtures()
        self._login("grandma")
    
    def test_normal_workflow(self):
        self._common()

    def tearDown(self):
        self.selenium.stop()


class TestAsAdmin(SeleniumTestBase, CommonTestsMixin):
    fixtures = ['addons/examiner/fixtures/selenium.json']

    def setUp(self):
        self.load_fixtures()
        self._login("scrooge")
    
    def test_normal_workflow(self):
        self._common()

    def tearDown(self):
        self.selenium.stop()


if __name__ == "__main__":
    unittest.main()
