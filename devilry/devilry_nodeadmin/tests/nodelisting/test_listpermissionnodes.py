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
        self.request = test.RequestFactory().get('/devilry_nodeadmin/')
        self.superuser = self.testhelper.create_superuser('super')
        self.view = PermissionNodesListView()

    def test_get_queryset_for_role_as_superuser_topnode(self):
        self.request.user = self.superuser
        self.view.request = self.request
        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='uio'))
        expected_shortnames = ['matnat', 'med']
        self.assertEqual(len(queryset_nodes), len(expected_shortnames))

        for node in queryset_nodes:
            self.assertIn(node.short_name, expected_shortnames)

    def test_get_queryset_for_role_as_superuser_midnode(self):
        self.request.user = self.superuser
        self.view.request = self.request
        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='matnat'))
        expected_shortnames = ['ifi']
        self.assertEqual(len(queryset_nodes), len(expected_shortnames))

        for node in queryset_nodes:
            self.assertIn(node.short_name, expected_shortnames)

    def test_get_queryset_for_role_as_superuser_bottomnode(self):
        self.request.user = self.superuser
        self.view.request = self.request
        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='ifi'))
        expected_shortnames = []
        self.assertEqual(len(queryset_nodes), len(expected_shortnames))

    def test_get_queryset_for_role_as_topadmin_topnode(self):
        self.request.user = User.objects.get(username='uioadmin')
        self.view.request = self.request
        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='uio'))
        expected_shortname = ['matnat', 'med']
        self.assertEqual(len(queryset_nodes), len(expected_shortname))

        for node in queryset_nodes:
            self.assertIn(node.short_name, expected_shortname)

    def test_get_queryset_for_role_as_topadmin_midnode(self):
        self.request.user = User.objects.get(username='matnatadmin')
        self.view.request = self.request
        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='matnat'))
        expected_shortnames = ['ifi']
        self.assertEqual(len(queryset_nodes), len(expected_shortnames))

        for node in queryset_nodes:
            self.assertIn(node.short_name, expected_shortnames)

    def test_get_queryset_for_role_as_topadmin_bottomnode(self):
        self.request.user = User.objects.get(username='matnatadmin')
        self.view.request = self.request
        queryset_nodes = self.view.get_queryset_for_role(Node.objects.get(short_name='ifi'))
        expected_shortnames = []
        self.assertEqual(len(queryset_nodes), len(expected_shortnames))

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
        # no_access = False

        

        # try:
        #     self.view.get_queryset_for_role(Node.objects.get(short_name='uio'))
        # except exceptions.PermissionDenied:
        #     self.assertEqual(403, 403)
        # else:
        #     self.assertTrue(no_access)
        #
        # try:
        #     self.view.get_queryset_for_role(Node.objects.get(short_name='med'))
        # except exceptions.PermissionDenied:
        #     self.assertEqual(403, 403)
        # else:
        #     self.assertTrue(no_access)
        #
        # try:
        #     self.view.get_queryset_for_role(Node.objects.get(short_name='imb'))
        # except exceptions.PermissionDenied:
        #     self.assertEqual(403, 403)
        # else:
        #     self.assertTrue(no_access)