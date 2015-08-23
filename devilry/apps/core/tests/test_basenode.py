from django.test import TestCase

from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from ..models import Node, Subject
from ..testhelper import TestHelper


class TestBaseNode(TestCase, TestHelper):
    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin,ifitechsupport)")
        self.add(nodes="uio.deepdummy1")
        self.thesuperuser = UserBuilder('thesuperuser', is_superuser=True).user

    def test_is_admin(self):
        self.assertTrue(self.uio.is_admin(self.uioadmin))
        self.assertFalse(self.uio.is_admin(self.ifiadmin))
        self.assertTrue(self.uio_ifi.is_admin(self.uioadmin))
        self.assertTrue(self.uio_ifi.is_admin(self.ifiadmin))

    def test_get_admins(self):
        def split_and_sort(admins):
            l = admins.split(', ')
            l.sort()
            return ', '.join(l)

        self.assertEquals(self.uio.get_admins(), 'uioadmin')
        self.assertEquals(split_and_sort(self.uio_ifi.get_admins()),
                          'ifiadmin, ifitechsupport')

    def test_can_save(self):
        self.assertTrue(self.uio.can_save(self.uioadmin))
        self.assertFalse(self.uio.can_save(self.ifiadmin))
        self.assertTrue(self.uio_ifi.can_save(self.ifiadmin))
        self.assertTrue(self.uio_ifi.can_save(self.uioadmin))

        self.assertTrue(Node().can_save(self.thesuperuser))
        self.assertFalse(Node(parentnode=None).can_save(self.uioadmin))
        self.assertTrue(Node(parentnode=self.uio).can_save(self.uioadmin))
        self.assertFalse(Node(parentnode=self.uio).can_save(self.ifiadmin))

    def test_can_save_id_none(self):
        self.assertTrue(Subject(parentnode=self.uio_deepdummy1).can_save(self.uioadmin))
        self.assertFalse(Subject(parentnode=self.uio_deepdummy1).can_save(self.ifiadmin))

    def test_get_inherited_admins(self):
        self.add(nodes='uio.matnat:admin(matnatadm).ifi:admin(ifiadmin,ifiadmin2)',
                 subjects=['duck2000:admin(duck2000adm)'],
                 periods=['aboutnow:admin(aboutnowadm)'])
        admins = [a.user for a in self.duck2000_aboutnow.get_inherited_admins()]
        self.assertEquals(len(admins), 5)
        self.assertTrue(self.duck2000adm in admins)
        self.assertTrue(self.uioadmin in admins)
        self.assertTrue(self.ifiadmin2 in admins)
        self.assertFalse(self.aboutnowadm in admins)

        admins = [a.user for a in self.uio_matnat_ifi.get_inherited_admins()]
        self.assertEquals(len(admins), 2)
        self.assertTrue(self.uioadmin in admins)
        self.assertTrue(self.matnatadm in admins)
        self.assertFalse(self.ifiadmin2 in admins)

        inherited_admins = self.duck2000_aboutnow.get_inherited_admins()
        inherited_admins.sort(cmp=lambda a, b: cmp(a.user.shortname, b.user.shortname))
        self.assertEquals(inherited_admins[0].user.shortname, 'duck2000adm')
        self.assertEquals(inherited_admins[0].basenode.short_name, 'duck2000')

    def test_get_all_admin_ids(self):
        self.add(nodes='uio.matnat:admin(matnatadm).ifi:admin(ifiadmin,ifiadmin2)',
                 subjects=['duck2000:admin(duck2000adm)'],
                 periods=['aboutnow:admin(aboutnowadm)'])

        admin_ids = self.duck2000_aboutnow.get_all_admin_ids()
        self.assertEquals(len(admin_ids), 6)
        self.assertEquals(admin_ids,
                          set([self.uioadmin.id, self.matnatadm.id, self.ifiadmin.id,
                               self.ifiadmin2.id, self.duck2000adm.id, self.aboutnowadm.id]))
