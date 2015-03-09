import os
import uuid
from django.conf import settings
from django.test import TestCase
from shutil import rmtree

from ..testhelpers import DeliveryStoreTestMixin
from ..deliverystore import DjangoStorageDeliveryStore


class TestDjangoStorageDeliveryStore(DeliveryStoreTestMixin, TestCase):
    def setUp(self):
        self.root = str(uuid.uuid1())
        self.tempdir = os.path.join(settings.MEDIA_ROOT, self.root)
        os.makedirs(self.tempdir)
        super(TestDjangoStorageDeliveryStore, self).setUp()

    def get_storageobj(self):
        return DjangoStorageDeliveryStore(self.root)

    def tearDown(self):
        rmtree(self.tempdir)
