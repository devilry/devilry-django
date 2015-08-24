from django.test import TestCase, RequestFactory

from devilry.apps.core.models import Node
from devilry.devilry_admin.views.node import crinstance_node
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, NodeBuilder


class TestCrAdminInstance(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.nodebuilder = NodeBuilder('ducku')
        self.childnodebuilder = self.nodebuilder\
            .add_childnode('middle')\
            .add_childnode('child')

    def test_error_if_not_admin(self):
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_node.CrAdminInstance(request=request)
        with self.assertRaises(Node.DoesNotExist):
            instance.get_role_from_rolequeryset(role=self.testuser)

    def test_admin_on_node(self):
        self.childnodebuilder.add_admins(self.testuser)
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_node.CrAdminInstance(request=request)
        self.assertEqual(
            instance.get_role_from_rolequeryset(role=self.childnodebuilder.node),
            self.childnodebuilder.node)

    def test_admin_on_parentnode(self):
        self.nodebuilder.add_admins(self.testuser)
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_node.CrAdminInstance(request=request)
        self.assertEqual(
            instance.get_role_from_rolequeryset(role=self.childnodebuilder.node),
            self.childnodebuilder.node)
