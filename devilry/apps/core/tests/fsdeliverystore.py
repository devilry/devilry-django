from django.test import TestCase
from tempfile import mkdtemp
from shutil import rmtree

from ..testhelpers import TestDeliveryStoreMixin
from ..deliverystore import FsDeliveryStore

class TestFsDeliveryStore(TestDeliveryStoreMixin, TestCase):
    def setUp(self):
        self.root = mkdtemp()
        super(TestFsDeliveryStore, self).setUp()

    def get_storageobj(self):
        return FsDeliveryStore(self.root)

    def tearDown(self):
        rmtree(self.root)
