from django.test import TestCase

from ..testhelpers import DeliveryStoreTestMixin
from ..deliverystore import MemoryDeliveryStore

class TestMemoryDeliveryStore(DeliveryStoreTestMixin, TestCase):
    def get_storageobj(self):
        return MemoryDeliveryStore()
