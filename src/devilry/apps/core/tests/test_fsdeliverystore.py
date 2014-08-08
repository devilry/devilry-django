from django.test import TestCase
from tempfile import mkdtemp
from shutil import rmtree

from ..testhelpers import DeliveryStoreTestMixin
from ..deliverystore import FsDeliveryStore

class TestFsDeliveryStore(DeliveryStoreTestMixin, TestCase):
    def setUp(self):
        self.root = mkdtemp()
        super(TestFsDeliveryStore, self).setUp()

    def get_storageobj(self):
        return FsDeliveryStore(self.root)

    def tearDown(self):
        rmtree(self.root)
