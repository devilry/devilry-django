from django.test import TestCase
from devilry.apps.core.testhelper import TestHelper
from devilry.apps.coredao.errors import NotPermittedToDeleteNonEmptyError
from devilry.apps.coredao.djangoorm.nodeadmin_required import NodeAdminRequiredError, nodeadmin_required
from devilry.apps.coredao.djangoorm.nodedao import NodeDao


class TestNodeDao(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes="rootnode.subnode:admin(normaluser).subsubnode.subsubsubnode")
        self.testhelper.add(nodes="rootnode.altsubnode.altsubsubnode:admin(normaluser)")
        self.testhelper.create_superuser("superuser")
        self.nodedao = NodeDao()

    def test_superuser(self):
        # The only difference for superuser is auth, so the normal user tests cover everything but these sanity tests
        self.nodedao.create(self.testhelper.superuser, 'tst', "Test")
        self.nodedao.create(self.testhelper.superuser, 'tst2', "Test2",
                            parentnode_id=self.testhelper.rootnode_subnode_subsubnode.id)

        self.nodedao.read(self.testhelper.superuser, self.testhelper.rootnode.id)
        self.nodedao.read(self.testhelper.superuser, self.testhelper.rootnode_subnode_subsubnode.id)

        self.nodedao.update(self.testhelper.superuser, self.testhelper.rootnode.id, 'tstupdated', "Test updated")
        self.nodedao.update(self.testhelper.superuser, self.testhelper.rootnode_subnode_subsubnode.id, 'tst2', "Test2",
                            parentnode_id=self.testhelper.rootnode_subnode.id)

        self.nodedao.delete(self.testhelper.superuser, self.testhelper.rootnode_subnode_subsubnode.id)
        self.nodedao.delete(self.testhelper.superuser, self.testhelper.rootnode.id)

    def test_create_normaluser(self):
        with self.assertRaises(NodeAdminRequiredError):
            self.nodedao.create(self.testhelper.normaluser,
                                'tst', 'Test', parentnode_id=self.testhelper.rootnode.id)

        nodedct = self.nodedao.create(self.testhelper.normaluser,
                                      'tst', 'Test', parentnode_id=self.testhelper.rootnode_subnode.id)
        del nodedct['id']
        self.assertEquals(nodedct, dict(long_name='Test', short_name='tst',
                                        parentnode_id=self.testhelper.rootnode_subnode.id))

    def test_read_normaluser(self):
        self.assertRaises(NodeAdminRequiredError, self.nodedao.read,
                          self.testhelper.normaluser, self.testhelper.rootnode.id)
        self.nodedao.read(self.testhelper.normaluser, self.testhelper.rootnode_subnode.id)
        self.nodedao.read(self.testhelper.normaluser, self.testhelper.rootnode_subnode_subsubnode.id)

    def test_update_normaluser(self):
        with self.assertRaises(NodeAdminRequiredError): # Update without changing parentnode
            self.nodedao.update(self.testhelper.normaluser,
                                self.testhelper.rootnode_subnode.id,
                                'tst', 'Test', parentnode_id=self.testhelper.rootnode_subnode.parentnode_id)

        nodedct = self.nodedao.update(self.testhelper.normaluser,
                                      self.testhelper.rootnode_subnode_subsubnode.id,
                                      'tst', 'Test', parentnode_id=self.testhelper.rootnode_subnode.id)
        self.assertEquals(nodedct, dict(id=self.testhelper.rootnode_subnode_subsubnode.id,
                                        long_name='Test', short_name='tst',
                                        parentnode_id=self.testhelper.rootnode_subnode.id))

    def test_move_normaluser(self):
        with self.assertRaises(NodeAdminRequiredError): # Update and move
            nodedct = self.nodedao.update(self.testhelper.normaluser,
                                          self.testhelper.rootnode_subnode_subsubnode.id,
                                          'tst', 'Test', parentnode_id=self.testhelper.rootnode_altsubnode.id)
        nodedct = self.nodedao.update(self.testhelper.normaluser,
                                      self.testhelper.rootnode_subnode_subsubnode.id,
                                      'tst', 'Test', parentnode_id=self.testhelper.rootnode_altsubnode_altsubsubnode.id)
        self.assertEquals(nodedct['parentnode_id'], self.testhelper.rootnode_altsubnode_altsubsubnode.id)


    def test_delete_normaluser(self):
        with self.assertRaises(NodeAdminRequiredError):
            self.nodedao.delete(self.testhelper.normaluser, self.testhelper.rootnode_subnode.id)
        with self.assertRaises(NotPermittedToDeleteNonEmptyError):
            self.nodedao.delete(self.testhelper.normaluser, self.testhelper.rootnode_subnode_subsubnode.id)
        self.nodedao.delete(self.testhelper.normaluser, self.testhelper.rootnode_subnode_subsubnode_subsubsubnode.id)
