from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssExists
from devilry_developer.testhelpers.login import LoginTestCaseMixin



class TestFrontpage(TestCase, LoginTestCaseMixin):
    def setUp(self):
        self.url = reverse('devilry_student')
        self.testuser = UserBuilder('testuser')

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_authenticated(self):
        response = self.get_as(self.testuser.user, self.url)
        self.assertEquals(response.status_code, 200)

    # def test_active_assignments(self):
    #     PeriodBuilder.quickadd_ducku_duck1010_active()\
    #         .add_assignment('week1')\
    #         .add_group(students=[self.testuser.user])
    #     html = self.get_as(self.testuser.user, self.url).content