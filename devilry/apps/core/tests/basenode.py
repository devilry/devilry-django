from django.contrib.auth.models import User

from django.test import TestCase
from ..models import Node, Subject

class TestBaseNode(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']

    def setUp(self):
        self.thesuperuser= User.objects.get(username='thesuperuser')
        self.uio = Node.objects.get(short_name='uio', parentnode=None)
        self.ifi = Node.objects.get(short_name='ifi', parentnode=self.uio)
        self.uioadmin = User.objects.get(username='uioadmin') # admin on the uio node
        self.ifiadmin = User.objects.get(username='ifiadmin') # admin on the ifi node

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
        deepdummy1 = Node.objects.get(pk=4)
        self.assertTrue(Subject(parentnode=deepdummy1).can_save(self.uioadmin))
        self.assertFalse(Subject(parentnode=deepdummy1).can_save(self.ifiadmin))
