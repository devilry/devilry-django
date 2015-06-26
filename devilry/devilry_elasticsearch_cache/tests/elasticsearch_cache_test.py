from django import test
from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_elasticsearch_cache import elasticsearch_cache as es_cache

class TestElasticsearchCache(test.TestCase):
    def setUp(self):
        self.testhelper = TestHelper()

    def test_elasticsearch_configuration_empty(self):
        es_cache.configure_elasticsearch()
        self.assertTrue(True, True)
