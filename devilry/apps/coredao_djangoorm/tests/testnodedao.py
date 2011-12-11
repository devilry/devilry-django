from datetime import datetime
from django.test import TestCase
from dingus import Dingus
from devilry.apps.core.testhelper import TestHelper
from devilry.apps.coredao.errors import PermissionDeniedError
from devilry.apps.coredao_djangoorm.nodedao import NodeDao


class TestNodeDao(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes="rootnode.subnode:admin(normaluser).subsubnode")
        self.testhelper.create_superuser("superuser")
        self.nodedao = NodeDao()

    def test_read_normaluser(self):
        self.assertRaises(PermissionDeniedError, self.nodedao.read,
                          self.testhelper.normaluser, self.testhelper.rootnode.id)
        self.nodedao.read(self.testhelper.normaluser, self.testhelper.rootnode_subnode.id)
        self.nodedao.read(self.testhelper.normaluser, self.testhelper.rootnode_subnode_subsubnode.id)

    def test_read_superuser(self):
        self.nodedao.read(self.testhelper.superuser, self.testhelper.rootnode.id)
        self.nodedao.read(self.testhelper.superuser, self.testhelper.rootnode_subnode_subsubnode.id)

    def test_update_normaluser(self):
        self.assertRaises(PermissionDeniedError, self.nodedao.update,
                          self.testhelper.normaluser,
                          self.testhelper.rootnode_subnode.id,
                          'tst', 'Test', parentnode_id=self.testhelper.rootnode.id)

        nodedct = self.nodedao.update(self.testhelper.normaluser,
                                      self.testhelper.rootnode_subnode_subsubnode.id,
                                      'tst', 'Test', parentnode_id=self.testhelper.rootnode_subnode.id)
        self.assertEquals(nodedct, dict(id=self.testhelper.rootnode_subnode_subsubnode.id,
                                        long_name='Test', short_name='tst',
                                        parentnode_id=self.testhelper.rootnode_subnode.id))