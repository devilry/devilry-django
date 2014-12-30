from django.test import TestCase
from devilry.apps.core.testhelper import TestHelper
from django.test.client import Client
from django.core.urlresolvers import reverse



class TestEmailSendingDebugView(TestCase):
    def setUp(self):
        self.client = Client()
        self.testhelper = TestHelper()
        self.nobody = self.testhelper.create_user('nobody')
        self.superuser = self.testhelper.create_superuser('superuser')
        self.url = reverse('send_email_to_students_email_sending_debug',
                           kwargs={'username': 'targetuser'})

    def test_email_sending_debug_nobody(self):
        self.client.login(username='nobody', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_email_sending_debug(self):
        self.testhelper.create_user('targetuser')
        self.client.login(username='superuser', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('<html>' in response.content)
        self.assertTrue('targetuser@example.com' in response.content)

    def test_email_sending_debug_invaliduser(self):
        self.client.login(username='superuser', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, 'ERROR: User "targetuser" does not exist')

    def test_email_sending_debug_noemail(self):
        targetuser = self.testhelper.create_user('targetuser')
        targetuser.email = ''
        targetuser.save()
        self.client.login(username='superuser', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'ERROR: User "targetuser" has no email address')

    def test_email_sending_debug_superuser_noemail(self):
        targetuser = self.testhelper.create_user('targetuser')
        superuser = self.testhelper.superuser
        superuser.email = ''
        superuser.save()
        self.client.login(username='superuser', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'ERROR: YOU (superuser) have no email address')
