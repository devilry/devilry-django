from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from devilry.project.develop.testhelpers.corebuilder import UserBuilder2


class TestEmailSendingDebugView(TestCase):
    def setUp(self):
        self.client = Client()

    def __getrequest(self, login_username, targetuser_pk):
        self.client.login(username=login_username, password='test')
        url = reverse('send_email_to_students_email_sending_debug',
                      kwargs={'pk': targetuser_pk})
        return self.client.get(url)

    def test_email_sending_debug_nobody(self):
        UserBuilder2(is_superuser=False)\
            .add_usernames('superuser')\
            .add_emails('superuser@example.com')
        targetuser = UserBuilder2(shortname='targetuser')\
            .add_emails('targetuser@example.com')\
            .user
        response = self.__getrequest(login_username='superuser',
                                     targetuser_pk=targetuser.pk)
        self.assertEqual(response.status_code, 403)

    def test_email_sending_debug(self):
        UserBuilder2(is_superuser=True)\
            .add_usernames('superuser')\
            .add_emails('superuser@example.com')
        targetuser = UserBuilder2(shortname='targetuser')\
            .add_emails('targetuser@example.com')\
            .user
        response = self.__getrequest(login_username='superuser',
                                     targetuser_pk=targetuser.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('<html>' in response.content)
        self.assertTrue('targetuser@example.com' in response.content)

    def test_email_sending_debug_invaliduser(self):
        UserBuilder2(is_superuser=True).add_usernames('superuser')
        response = self.__getrequest(login_username='superuser',
                                     targetuser_pk=10000000001)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, 'ERROR: User "#10000000001" does not exist')

    def test_email_sending_debug_targetuser_noemail(self):
        UserBuilder2(is_superuser=True)\
            .add_usernames('superuser')\
            .add_emails('superuser@example.com')
        targetuser = UserBuilder2(shortname='targetuser').user
        response = self.__getrequest(login_username='superuser',
                                     targetuser_pk=targetuser.pk)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'ERROR: User "targetuser" has no email address')

    def test_email_sending_debug_superuser_noemail(self):
        UserBuilder2(shortname='thesuperuser', is_superuser=True).add_usernames('superuser')
        targetuser = UserBuilder2().add_emails('test@example.com').user
        response = self.__getrequest(login_username='superuser',
                                     targetuser_pk=targetuser.pk)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'ERROR: YOU (thesuperuser) have no email address')
