from mock import Mock
from django.test import TestCase
from bs4 import BeautifulSoup

# from develop.testhelpers.soupselect import cssGet
# from develop.testhelpers.soupselect import cssExists
from devilry.project.develop.testhelpers.soupselect import normalize_whitespace
from devilry.devilry_student.templatetags.devilry_student_tags import devilry_student_shortgrade

class TestDevilryStudentFeedbackTags(TestCase):
    def setUp(self):
        pass

    def test_passed_with_grade(self):
        feedback = Mock()
        feedback.grade = 'A'
        feedback.is_passing_grade = True
        self.assertEqual(
            normalize_whitespace(BeautifulSoup(devilry_student_shortgrade(feedback)).text),
            'A (Passed)'
        )

    def test_failed_with_grade(self):
        feedback = Mock()
        feedback.grade = 'F'
        feedback.is_passing_grade = False
        self.assertEqual(
            normalize_whitespace(BeautifulSoup(devilry_student_shortgrade(feedback)).text),
            'F (Failed)'
        )

    def test_passed(self):
        feedback = Mock()
        feedback.grade = 'Passed'
        feedback.is_passing_grade = True
        self.assertEqual(
            normalize_whitespace(BeautifulSoup(devilry_student_shortgrade(feedback)).text),
            'Passed'
        )

    def test_failed(self):
        feedback = Mock()
        feedback.grade = 'Failed'
        feedback.is_passing_grade = False
        self.assertEqual(
            normalize_whitespace(BeautifulSoup(devilry_student_shortgrade(feedback)).text),
            'Failed'
        )
