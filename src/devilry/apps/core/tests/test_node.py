from datetime import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import Node
from ..testhelper import TestHelper
from ..models.model_utils import EtagMismatchException

class TestNode(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)")
        self.add(nodes="uio.phys")
        self.add(nodes="uio.deepdummy1:admin(deepdummyadmin).deepdummy2.deepdummy3")

    def test_unique(self):
        n = Node(parentnode=self.uio_deepdummy1, short_name='ifi', long_name='Ifi')
        n.save()
        n.parentnode = self.uio
        self.assertRaises(IntegrityError, n.save)

    def test_unique_noneparent(self):
        n = Node(parentnode=None, short_name='stuff', long_name='Ifi')
        n.clean()
        n.save()
        n2 = Node(parentnode=None, short_name='stuff', long_name='Ifi')
        self.assertRaises(ValidationError, n2.clean)

    def test_can_save(self):
        self.assertFalse(Node().can_save(self.ifiadmin))

    def test_etag_update(self):
        etag = datetime.now()
        obj = self.uio
        obj.long_name = "Test"
        self.assertRaises(EtagMismatchException, obj.etag_update, etag)
        try:
            obj.etag_update(etag)
        except EtagMismatchException as e:
            # Should not raise exception
            obj.etag_update(e.etag)
        obj2 = Node.objects.get(id=obj.id)
        self.assertEquals(obj2.long_name, "Test")

    def test_short_name_validation(self):
        self.uio.short_name = '1'
        self.uio.full_clean()
        self.uio.short_name = '_'
        self.uio.full_clean()
        self.uio.short_name = '-'
        self.uio.full_clean()
        self.uio.short_name = 'u'
        self.uio.full_clean()
        self.uio.short_name = 'u-i_o--0'
        self.uio.full_clean()
        self.uio.short_name = 'L'
        self.assertRaises(ValidationError, self.uio.full_clean)

    def test_unicode(self):
        self.assertEquals(unicode(self.uio_deepdummy1_deepdummy2_deepdummy3),
                'uio.deepdummy1.deepdummy2.deepdummy3')

    def test_get_path(self):
        self.assertEquals(self.uio.get_path(), 'uio')
        self.assertEquals(self.uio_ifi.get_path(), 'uio.ifi')
        self.assertEquals(self.uio_deepdummy1_deepdummy2_deepdummy3.get_path(),
                          'uio.deepdummy1.deepdummy2.deepdummy3')

    def test_iter_childnodes(self):
        self.assertEquals(
                [n.short_name for n in self.uio_deepdummy1.iter_childnodes()],
                [u'deepdummy2', u'deepdummy3'])
        s = set([n.short_name for n in self.uio.iter_childnodes()])
        self.assertEquals(s, set([u'deepdummy1', u'deepdummy2', u'deepdummy3', u'phys', u'ifi']))

    def test_clean_parent_is_child(self):
        """ Can not be child of it's own child. """
        self.uio.parentnode = self.uio_ifi
        self.assertRaises(ValidationError, self.uio.clean)

    def test_clean_parent_is_self(self):
        """ Can not be child of itself. """
        self.uio.parentnode = self.uio
        self.assertRaises(ValidationError, self.uio.clean)

    def test_clean_noerrors(self):
        self.uio_ifi.clean()

    def test_create_multiple_roots(self):
        n = Node(short_name='test', long_name='Test', parentnode=None)
        n.clean()
        n.save()
        n2 = Node(short_name='test2', long_name='Test2', parentnode=None)
        n2.clean()
        n2.save()

    def test_where_is_admin(self):
        self.assertEquals(Node.where_is_admin(self.uioadmin).count(), 6)
        self.assertEquals(Node.where_is_admin(self.ifiadmin).count(), 1)

    def test_get_nodepks_where_is_admin(self):
        self.add(nodes="uio.matnat.math:admin(testadmin)")
        self.add(nodes="uio.matnat.phys.test1:admin(testadmin)")
        self.add(nodes="uio.matnat.chem:admin(testadmin)")
        self.add(nodes="uio.matnat.bio:admin(testadmin)")
        self.add(nodes="uio.matnat.bio.test1")

        pk_verify = []
        pk_verify.append(self.uio_matnat_math.id)
        pk_verify.append(self.uio_matnat_phys_test1.id)
        pk_verify.append(self.uio_matnat_chem.id)
        pk_verify.append(self.uio_matnat_bio.id)
        pk_verify.append(self.uio_matnat_bio_test1.id)

        testadmin = User.objects.get(username='testadmin')
        pks = Node._get_nodepks_where_isadmin(testadmin)
        pks.sort()
        pk_verify.sort()
        self.assertEquals(set(pks), set(pk_verify))

    def test_is_empty(self):
        self.assertTrue(self.uio_ifi.is_empty())
        self.assertFalse(self.uio.is_empty())
        self.add(nodes="uio.ifi", subjects=['duck1010'])
        self.assertFalse(self.uio_ifi.is_empty())

    def test_can_delete(self):
        self.create_superuser('grandma')
        self.assertTrue(self.uio_deepdummy1_deepdummy2_deepdummy3.can_delete(self.deepdummyadmin)) # Admin on parent, and empty
        self.assertFalse(self.uio_deepdummy1_deepdummy2.can_delete(self.deepdummyadmin)) # Not empty (contains childnodes)

        self.assertTrue(self.uio_ifi.can_delete(self.grandma)) # Superadmin
        self.assertFalse(self.uio_ifi.can_delete(self.ifiadmin)) # Not admin on parentnode
        self.assertTrue(self.uio_ifi.can_delete(self.uioadmin)) # Admin on parentnode
        self.add(nodes="uio.ifi", subjects=['duck1010'])
        self.assertFalse(self.uio_ifi.can_delete(self.uioadmin)) # Not empty (contains a subject)
