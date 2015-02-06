from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder
from devilry.project.develop.testhelpers.corebuilder import NodeBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssExists
from devilry.project.develop.testhelpers.login import LoginTestCaseMixin


class TestFrontpage(TestCase, LoginTestCaseMixin):
    def setUp(self):
        self.url = reverse('devilry_frontpage')
        self.testuser = UserBuilder('testuser')

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_authenticated(self):
        response = self.get_as(self.testuser.user, self.url)
        self.assertEquals(response.status_code, 200)
    
    def test_roleselect_student(self):
        PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1')\
            .add_group(students=[self.testuser.user])
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(len(cssFind(html, '#devilry_frontpage_roleselect_list a')), 1)
        self.assertTrue(cssExists(html, '#devilry_frontpage_roleselect_student'))

    def test_roleselect_examiner(self):
        PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('week1')\
            .add_group(examiners=[self.testuser.user])
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(len(cssFind(html, '#devilry_frontpage_roleselect_list a')), 1)
        self.assertTrue(cssExists(html, '#devilry_frontpage_roleselect_examiner'))

    def test_roleselect_subjectadmin(self):
        SubjectBuilder.quickadd_ducku_duck1010().add_admins(self.testuser.user)
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(len(cssFind(html, '#devilry_frontpage_roleselect_list a')), 1)
        self.assertTrue(cssExists(html, '#devilry_frontpage_roleselect_subjectadmin'))

    def test_roleselect_nodeadmin(self):
        NodeBuilder('univ').add_admins(self.testuser.user)
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(len(cssFind(html, '#devilry_frontpage_roleselect_list a')), 1)
        self.assertTrue(cssExists(html, '#devilry_frontpage_roleselect_nodeadmin'))

    def test_roleselect_superuser(self):
        self.testuser.update(is_superuser=True, is_staff=True)
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(len(cssFind(html, '#devilry_frontpage_roleselect_list a')), 2)
        self.assertTrue(cssExists(html, '#devilry_frontpage_roleselect_nodeadmin'))
        self.assertTrue(cssExists(html, '#devilry_frontpage_roleselect_superuser'))

    def test_roleselect_superuser_not_staff(self):
        self.testuser.update(is_superuser=True, is_staff=False)
        html = self.get_as(self.testuser.user, self.url).content
        self.assertEquals(len(cssFind(html, '#devilry_frontpage_roleselect_list a')), 1)
        self.assertTrue(cssExists(html, '#devilry_frontpage_roleselect_nodeadmin'))
        self.assertFalse(cssExists(html, '#devilry_frontpage_roleselect_superuser'))

    def test_lacking_permissions_message(self):
        with self.settings(DEVILRY_LACKING_PERMISSIONS_URL='http://example.com/a/test'):
            html = self.get_as(self.testuser.user, self.url).content
            self.assertEquals(
                cssGet(html, '#devilry_frontpage_lacking_permissions_link')['href'],
                'http://example.com/a/test')
            self.assertEquals(
                cssGet(html, '#devilry_frontpage_lacking_permissions_link').text.strip(),
                'I should have had more roles')
