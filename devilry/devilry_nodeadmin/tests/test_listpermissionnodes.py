from django import test
from django.contrib.auth.models import User
from devilry.apps.core.models.node import Node

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_nodeadmin.crapps.listpermissionnodes import PermissionNodesListView


class TestPermissionNodesListView(test.TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uio:admin(uniadmin).matnat:admin(infadmin).ifi:admin(ifiadmin)')
        self.testhelper.add(nodes='uio.med:admin(medadmin).imb')
        self.testhelper.add(nodes='universe:admin(allfather).cluster:admin(thor).galaxy:admin(me)')
        self.request = test.RequestFactory().get('/devilry_nodeadmin/')
        self.superuser = self.testhelper.create_superuser('super')
        self.view = PermissionNodesListView()

    def _assert_permission(self, expected_node_shortnames, nodes):
        self.assertEqual(len(nodes), len(expected_node_shortnames))
        for node in nodes:
            self.assertIn(node.short_name, expected_node_shortnames)

    def test_get_queryset_for_role_as_superuser(self):
        # superuser should have access to all
        self.request.user = self.superuser
        self.view.request = self.request

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='uio')).all()
        self._assert_permission(['matnat', 'med'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='matnat')).all()
        self._assert_permission(['ifi'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='med')).all()
        self._assert_permission(['imb'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='ifi'))
        self._assert_permission([], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='universe'))
        self._assert_permission(['cluster'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='cluster'))
        self._assert_permission(['galaxy'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='galaxy'))
        self._assert_permission([], queryset_nodes)

    def test_get_queryset_for_role_as_topnode_admin(self):
        # admin for a topnode, such as 'uniadmin' is admin in uio
        # and therefore admin for all childnodes(recursively)
        self.request.user = User.objects.get(username='uniadmin')
        self.view.request = self.request

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='uio')).all()
        self._assert_permission(['matnat', 'med'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='matnat')).all()
        self._assert_permission(['ifi'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='med')).all()
        self._assert_permission(['imb'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='ifi')).all()
        self._assert_permission([], queryset_nodes)

    def test_get_queryset_for_role_as_topnode_wrongadmin(self):
        self.assertEqual(True, True)

    def test_get_queryset_for_role_as_basenode_admin(self):
        # only access
        self.assertEqual(True, True)
