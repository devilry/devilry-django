from django.contrib.auth.models import User

from django.test import TestCase
from ..models import Node, Subject
from ..testhelper import TestHelper

class TestBaseNode(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin,ifitechsupport)")
        self.add(nodes="uio.deepdummy1")
        self.thesuperuser = User.objects.create(username='thesuperuser', is_superuser=True)

    def test_is_admin(self):
        self.assertTrue(self.uio.is_admin(self.uioadmin))
        self.assertFalse(self.uio.is_admin(self.ifiadmin))
        self.assertTrue(self.ifi.is_admin(self.uioadmin))
        self.assertTrue(self.ifi.is_admin(self.ifiadmin))

    def test_get_admins(self):
        def split_and_sort(admins):
            l = admins.split(', ')
            l.sort()
            return ', '.join(l)
        self.assertEquals(self.uio.get_admins(), 'uioadmin')
        self.assertEquals(split_and_sort(self.ifi.get_admins()),
                'ifiadmin, ifitechsupport')

    def test_can_save(self):
        self.assertTrue(self.uio.can_save(self.uioadmin))
        self.assertFalse(self.uio.can_save(self.ifiadmin))
        self.assertTrue(self.ifi.can_save(self.ifiadmin))
        self.assertTrue(self.ifi.can_save(self.uioadmin))

        self.assertTrue(Node().can_save(self.thesuperuser))
        self.assertFalse(Node(parentnode=None).can_save(self.uioadmin))
        self.assertTrue(Node(parentnode=self.uio).can_save(self.uioadmin))
        self.assertFalse(Node(parentnode=self.uio).can_save(self.ifiadmin))

    def test_can_save_id_none(self):
        self.assertTrue(Subject(parentnode=self.deepdummy1).can_save(self.uioadmin))
        self.assertFalse(Subject(parentnode=self.deepdummy1).can_save(self.ifiadmin))
