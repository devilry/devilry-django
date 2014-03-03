from django.test import TestCase

from devilry.apps.core.tests.devilry_core_testapp.models import BulkCreateIdentifierDemoModel


class TestBulkCreateIdentifier(TestCase):
    def test_sanity(self):
        self.assertEquals(BulkCreateIdentifierDemoModel.objects.count(), 0)
        createdA = BulkCreateIdentifierDemoModel.objects.create_many('Test One', 'Test Two')
        createdB = BulkCreateIdentifierDemoModel.objects.create_many('Test Three')
        self.assertEquals(BulkCreateIdentifierDemoModel.objects.count(), 3)
        self.assertEquals(createdA.count(), 2)
        self.assertEquals(set([c.name for c in createdA]), set(['Test One', 'Test Two']))