from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from model_mommy import mommy

from devilry.devilry_account.models import UserEmail, UserName
from devilry.utils import anonymize_database


class TestAnonymizeUserFast(test.TestCase):
    def test_anonymize_user_shortname(self):
        mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        self.assertEqual(get_user_model().objects.first().shortname, 'testuser')
        anonymize_database.anonymize_user()
        self.assertEqual(get_user_model().objects.first().shortname,
                         str(get_user_model().objects.get().id))

    def test_anonymize_user_email(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        mommy.make('devilry_account.UserEmail', email='testuser@example.com', user=testuser)
        self.assertEqual(UserEmail.objects.get().email, 'testuser@example.com')
        anonymize_database.anonymize_user()
        self.assertEqual(UserEmail.objects.get().email,
                         '{}{}'.format(get_user_model().objects.get().id, '@example.com'))

    def test_anonymize_user_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        mommy.make('devilry_account.UserName', username='testuser', user=testuser)
        self.assertEqual(UserName.objects.get().username, 'testuser')
        anonymize_database.anonymize_user()
        self.assertEqual(UserName.objects.get().username,
                         str(get_user_model().objects.get().id))

    def test_anonymize_multiple_users(self):
        testuser1 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser1')
        testuser2 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser2')
        testuser3 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser3')
        self.assertEqual(get_user_model().objects.filter(shortname='testuser1').count(), 1)
        self.assertEqual(get_user_model().objects.filter(shortname='testuser2').count(), 1)
        self.assertEqual(get_user_model().objects.filter(shortname='testuser3').count(), 1)
        anonymize_database.anonymize_user()
        self.assertEqual(
            get_user_model().objects.get(id=testuser1.id).shortname,
            str(testuser1.id))
        self.assertEqual(
            get_user_model().objects.get(id=testuser2.id).shortname,
            str(testuser2.id))
        self.assertEqual(
            get_user_model().objects.get(id=testuser3.id).shortname,
            str(testuser3.id))

    def test_anonymize_multiple_user_emails(self):
        testemail1 = mommy.make('devilry_account.UserEmail', email='testemail1@example.com')
        testemail2 = mommy.make('devilry_account.UserEmail', email='testemail2@example.com')
        testemail3 = mommy.make('devilry_account.UserEmail', email='testemail3@example.com')
        self.assertEqual(UserEmail.objects.filter(email='testemail1@example.com').count(), 1)
        self.assertEqual(UserEmail.objects.filter(email='testemail2@example.com').count(), 1)
        self.assertEqual(UserEmail.objects.filter(email='testemail3@example.com').count(), 1)
        anonymize_database.anonymize_user()
        self.assertEqual(
            UserEmail.objects.get(id=testemail1.id).email,
            '{}@example.com'.format(testemail1.user.id))
        self.assertEqual(
            UserEmail.objects.get(id=testemail2.id).email,
            '{}@example.com'.format(testemail2.user.id))
        self.assertEqual(
            UserEmail.objects.get(id=testemail3.id).email,
            '{}@example.com'.format(testemail3.user.id))

    def test_anonymize_multiple_user_names(self):
        testusername1 = mommy.make('devilry_account.UserName', username='testusername1')
        testusername2 = mommy.make('devilry_account.UserName', username='testusername2')
        testusername3 = mommy.make('devilry_account.UserName', username='testusername3')
        self.assertEqual(UserName.objects.filter(username='testusername1').count(), 1)
        self.assertEqual(UserName.objects.filter(username='testusername2').count(), 1)
        self.assertEqual(UserName.objects.filter(username='testusername3').count(), 1)
        anonymize_database.anonymize_user()
        self.assertEqual(
            UserName.objects.get(id=testusername1.id).username,
            str(testusername1.user.id))
        self.assertEqual(
            UserName.objects.get(id=testusername2.id).username,
            str(testusername2.user.id))
        self.assertEqual(
            UserName.objects.get(id=testusername3.id).username,
            str(testusername3.user.id))

