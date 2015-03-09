"""Tests for the djangorestframework package setup."""
from django.test import TestCase
from devilry.thirdpartylibs import djangorestframework

class TestVersion(TestCase):
    """Simple sanity test to check the VERSION exists"""

    def test_version(self):
        """Ensure the VERSION exists."""
        djangorestframework.VERSION

