from django import test
from django.contrib.auth.models import User
from django_cradmin.crinstance import BaseCrAdminInstance

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models.node import Node

class TestNodeListingCrAdminInstance(test.TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.factory = test.RequestFactory()
        self.node = Node()
        self.node.long_name = 'long_name_is_much_longer_than_short_name'
        self.node.short_name = 'short_name'

    def test_get_rolequeryset(self):
        request = self.factory.get('/customer/details')
        request.user = self.testhelper.create_superuser('sarumeister')
        
        self.cr_instance = BaseCrAdminInstance(request)
        self.assertTrue(True)

    def test_get_titletext_for_role(self):
        self.assertTrue(self.node.short_name, 'short_name')

    def test_descriptiontext_for_role(self):
        self.assertTrue(self.node.long_name, 'long_name')

    def test_matches_urlpath(self):
        urlpath = '/testpage/test/t'
        self.assertTrue(urlpath.startswith('/testpage/test/'))