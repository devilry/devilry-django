from django import test
from django.contrib.auth.models import User
from django.core import exceptions

from devilry.apps.core.models.node import Node
from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_nodeadmin.crapps.listpermissionnodes import PermissionNodesListView


class TestPermissionNodesListView(test.TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uio:admin(uioadmin).matnat:admin(matnatadmin).ifi')
        self.testhelper.add(nodes='uio.med.imb')
        self.testhelper.add(nodes='universe:admin(allfather).cluster.galaxy')
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

        print self.view.get_queryset_for_role(Node.objects.get(short_name='uio'))

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='uio'))
        self._assert_permission(['matnat', 'med'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='matnat'))
        self._assert_permission(['ifi'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='med'))
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

        # test as uioadmin
        self.request.user = User.objects.get(username='uioadmin')
        self.view.request = self.request

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='uio'))
        self._assert_permission(['matnat', 'med'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='matnat'))
        self._assert_permission(['ifi'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='med'))
        self._assert_permission(['imb'], queryset_nodes)

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='ifi'))
        self._assert_permission([], queryset_nodes)

    def test_get_queryset_for_role_as_subnode_admin(self):
        # only access
        self.request.user = User.objects.get(username='matnatadmin')
        self.view.request = self.request

        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='matnat'))
        self._assert_permission(['ifi'], queryset_nodes)

    def test_get_queryset_for_role_as_wrongadmin(self):
        # test is passed when a permissionDenied exception is raised for every test
        self.request.user = User.objects.get(username='matnatadmin')
        self.view.request = self.request
        no_access = False

        try:
            self.view.get_queryset_for_role(Node.objects.get(short_name='uio'))
        except exceptions.PermissionDenied:
            self.assertEqual(403, 403)
        else:
            self.assertTrue(no_access)

        try:
            self.view.get_queryset_for_role(Node.objects.get(short_name='med'))
        except exceptions.PermissionDenied:
            self.assertEqual(403, 403)
        else:
            self.assertTrue(no_access)

        try:
            self.view.get_queryset_for_role(Node.objects.get(short_name='universe'))
        except exceptions.PermissionDenied:
            self.assertEqual(403, 403)
        else:
            self.assertTrue(no_access)

        try:
            self.view.get_queryset_for_role(Node.objects.get(short_name='imb'))
        except exceptions.PermissionDenied:
            self.assertEqual(403, 403)
        else:
            self.assertTrue(no_access)

        try:
            self.view.get_queryset_for_role(Node.objects.get(short_name='cluster'))
        except exceptions.PermissionDenied:
            self.assertEqual(403, 403)
        else:
            self.assertTrue(no_access)

        try:
            self.view.get_queryset_for_role(Node.objects.get(short_name='galaxy'))
        except exceptions.PermissionDenied:
            self.assertEqual(403, 403)
        else:
            self.assertTrue(no_access)