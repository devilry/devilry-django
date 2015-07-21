from django import test
from django.contrib.auth.models import User

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_nodeadmin.cradmin import NodeListingCrAdminInstance


class TestNodeListingCrAdminInstance(test.TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin).inf:admin(infadmin).inf_sub')
        self.testhelper.add(nodes='unifuzz:admin(fuzzyadmin)')
        self.request = test.RequestFactory().get('/devilry_nodeadmin/')
        self.superuser = self.testhelper.create_superuser('super')
        self.cr_instance = NodeListingCrAdminInstance(self.request)
        self.test_node = self.testhelper._create_or_add_node(None, 'test_node', {'admin':['saruman'], 'ln': None})

    def test_get_rolequeryset_as_superuser(self):
        # superuser has access to all nodes
        self.request.user = self.superuser
        queryset = self.cr_instance.get_rolequeryset()
        expected_shortnames = ['uni', 'unifuzz', 'inf', 'inf_sub', 'test_node']
        nodes = queryset.all()
        self.assertEqual(len(nodes), len(expected_shortnames))

        for node in nodes:
            self.assertIn(node.short_name, expected_shortnames)

    def test_get_rolequeryset_as_basenodeadmin_top(self):
        # basenodeadmin has access to node it belongs to and all subnodes
        self.request.user = User.objects.get(username='uniadmin')
        queryset = self.cr_instance.get_rolequeryset()
        expected_shortnames = ['uni', 'inf', 'inf_sub']
        nodes = queryset.all()
        self.assertEqual(len(nodes), len(expected_shortnames))

        for node in nodes:
            self.assertIn(node.short_name, expected_shortnames)

    def test_get_rolequeryset_as_basenodeadmin_sub(self):
        # infadmin has access to inf and all subnodes
        self.request.user = User.objects.get(username='infadmin')
        queryset = self.cr_instance.get_rolequeryset()
        expected_shortnames = ['inf', 'inf_sub']
        nodes = queryset.all()
        self.assertEqual(len(nodes), len(expected_shortnames))

        for node in nodes:
            self.assertIn(node.short_name, expected_shortnames)

    def test_get_rolequeryset_as_testnode_admin(self):
        # saruman has access only to 'test_node'
        self.request.user = User.objects.get(username='saruman')
        queryset = self.cr_instance.get_rolequeryset()
        expected_shortnames = ['test_node']
        nodes = queryset.all()
        self.assertEqual(len(nodes), len(expected_shortnames))

        for node in nodes:
            self.assertIn(node.short_name, expected_shortnames)

    def test_get_rolequeryset_as_nobody(self):
        # user 'nobody' should not have access to anything
        user = self.testhelper.create_user('nobody')
        self.request.user = user
        queryset = self.cr_instance.get_rolequeryset()
        self.assertEqual(0, queryset.count())

    def test_get_titletext_for_role(self):
        self.assertEquals(self.test_node.short_name, self.cr_instance.get_titletext_for_role(self.test_node))

    def test_descriptiontext_for_role(self):
        self.assertEquals(self.test_node.long_name, self.cr_instance.get_descriptiontext_for_role(self.test_node))
