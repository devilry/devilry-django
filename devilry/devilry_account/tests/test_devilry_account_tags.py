import htmls
from django import test
from django.conf import settings
from django.template.loader import render_to_string
from model_bakery import baker

from devilry.devilry_account.templatetags import devilry_account_tags


class TestDevilryUserVerboseInline(test.TestCase):
    def test_no_fullname_cssclass(self):
        testuser = baker.make(settings.AUTH_USER_MODEL,
                              fullname='')
        selector = htmls.S(
            render_to_string('devilry_account/templatetags/user-verbose-inline.django.html',
                             devilry_account_tags.devilry_user_verbose_inline(testuser)))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-shortnameonly'))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-both'))

    def test_no_fullname_text(self):
        testuser = baker.make(settings.AUTH_USER_MODEL,
                              fullname='',
                              shortname='testuser')
        selector = htmls.S(
            render_to_string('devilry_account/templatetags/user-verbose-inline.django.html',
                             devilry_account_tags.devilry_user_verbose_inline(testuser)))
        self.assertEqual('testuser',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_with_fullname_cssclass(self):
        testuser = baker.make(settings.AUTH_USER_MODEL,
                              fullname='Test User')
        selector = htmls.S(
            render_to_string('devilry_account/templatetags/user-verbose-inline.django.html',
                             devilry_account_tags.devilry_user_verbose_inline(testuser)))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-shortnameonly'))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-both'))

    def test_with_fullname_text(self):
        testuser = baker.make(settings.AUTH_USER_MODEL,
                              fullname='Test User',
                              shortname='testuser')
        selector = htmls.S(
            render_to_string('devilry_account/templatetags/user-verbose-inline.django.html',
                             devilry_account_tags.devilry_user_verbose_inline(testuser)))
        self.assertEqual('Test User',
                         selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized)
        self.assertEqual('(testuser)',
                         selector.one('.devilry-user-verbose-inline-shortname').alltext_normalized)
        self.assertEqual('Test User(testuser)',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)


class TestDevilryMultipleUsersVerboseInline(test.TestCase):
    def test_no_fullname_cssclass(self):
        testuser = baker.make(settings.AUTH_USER_MODEL,
                              fullname='')
        selector = htmls.S(
            render_to_string('devilry_account/templatetags/multiple-users-verbose-inline.django.html',
                             devilry_account_tags.devilry_multiple_users_verbose_inline([testuser])))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-shortnameonly'))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-both'))

    def test_no_fullname_text(self):
        testuser = baker.make(settings.AUTH_USER_MODEL,
                              fullname='',
                              shortname='testuser')
        selector = htmls.S(
            render_to_string('devilry_account/templatetags/multiple-users-verbose-inline.django.html',
                             devilry_account_tags.devilry_multiple_users_verbose_inline([testuser])))
        self.assertEqual('testuser',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_with_fullname_cssclass(self):
        testuser = baker.make(settings.AUTH_USER_MODEL,
                              fullname='Test User')
        selector = htmls.S(
            render_to_string('devilry_account/templatetags/multiple-users-verbose-inline.django.html',
                             devilry_account_tags.devilry_multiple_users_verbose_inline([testuser])))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-shortnameonly'))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline-both'))

    def test_with_fullname_text(self):
        testuser = baker.make(settings.AUTH_USER_MODEL,
                              fullname='Test User',
                              shortname='testuser')
        selector = htmls.S(
            render_to_string('devilry_account/templatetags/multiple-users-verbose-inline.django.html',
                             devilry_account_tags.devilry_multiple_users_verbose_inline([testuser])))
        self.assertEqual('Test User',
                         selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized)
        self.assertEqual('(testuser)',
                         selector.one('.devilry-user-verbose-inline-shortname').alltext_normalized)
        self.assertEqual('Test User(testuser)',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_multiple(self):
        testuser1 = baker.make(settings.AUTH_USER_MODEL,
                               shortname='testuser1')
        testuser2 = baker.make(settings.AUTH_USER_MODEL,
                               shortname='testuser2')
        selector = htmls.S(
            render_to_string('devilry_account/templatetags/multiple-users-verbose-inline.django.html',
                             devilry_account_tags.devilry_multiple_users_verbose_inline(
                                 [testuser1, testuser2])))
        shortnames = [element.alltext_normalized
                      for element in selector.list('.devilry-user-verbose-inline')]
        self.assertEqual(['testuser1', 'testuser2'], shortnames)
