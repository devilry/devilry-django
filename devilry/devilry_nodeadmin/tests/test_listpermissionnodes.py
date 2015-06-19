from django import test

from devilry.apps.core.models import Node


class TestPermissionNodesListView(test.TestCase):
    def setUp(self):
        self.node = Node()

    def test_get_queryset_for_role(self):
