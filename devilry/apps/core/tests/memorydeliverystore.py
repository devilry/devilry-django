from django.test import TestCase

from ..testhelpers import TestDeliveryStoreMixin
from ..deliverystore import MemoryDeliveryStore

class TestMemoryDeliveryStore(TestDeliveryStoreMixin, TestCase):
    def get_storageobj(self):
        return MemoryDeliveryStore()
