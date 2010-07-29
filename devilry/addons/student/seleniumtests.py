"""
Here are selenium tests for student
"""

from django.test import TestCase
from selenium import selenium
import unittest, time, re

class StudentDeliveryTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_delivery(self):
        sel = self.selenium
        sel.open("/ui/login?next=/")
        sel.type("id_username", "student1")
        sel.type("id_password", "test")
        sel.click("login")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Add Delivery"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Add Delivery")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Week 1 (student1)")
        sel.wait_for_page_to_load("30000")
        sel.type("id_form-0-file", "/home/bro/a.txt")
        sel.click("deliver")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Successful delivery"))
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
