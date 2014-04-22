from django.test import TestCase

# from devilry_developer.testhelpers.corebuilder import SubjectBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssExists



class TestFrontpage(TestCase):
    def setUp(self):
        self.url = reverse('devilry_frontpage')
    
    def test_helplinks(self):
        response = self.client.get(self.url)