from django.test import TestCase
from devilry.apps.core.testhelper import TestHelper
from devilry.apps.coredao.errors import PermissionDeniedError
from devilry.apps.coredao.djangoorm.nodedao import nodeadmin_required



class TestNodeAdminRequired(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes="tstnode.subnode:admin(normaluser)")
        self.testhelper.create_superuser("superuser")

    def test_nodeadmin_required_superuser(self):
        nodeadmin_required(self.testhelper.superuser, "", None ) # Calls is_superuser and exits without further checks

    def test_nodeadmin_required_normaluser(self):
        nodeadmin_required(self.testhelper.normaluser, "", self.testhelper.tstnode_subnode.id)

    def test_nodeadmin_required_normaluser_denied(self):
        self.assertRaises(PermissionDeniedError, nodeadmin_required, self.testhelper.normaluser, "", self.testhelper.tstnode.id)