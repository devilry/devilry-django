from django.test import TestCase
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join

from ..testhelpers import TestDeliveryStoreMixin
from ..deliverystore import DbmDeliveryStore

class TestDbmDeliveryStore(TestDeliveryStoreMixin, TestCase):
    def setUp(self):
        self.root = mkdtemp()
        super(TestDbmDeliveryStore, self).setUp()

    def get_storageobj(self):
        return DbmDeliveryStore(join(self.root, 'test.dbm'))

    def tearDown(self):
        rmtree(self.root)
