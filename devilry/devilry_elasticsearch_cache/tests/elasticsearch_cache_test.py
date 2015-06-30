from django import test

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_elasticsearch_cache import elasticsearch_cache as es_cache
from devilry.devilry_elasticsearch_cache import generate_nodes

class TestElasticsearchCache(test.TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.node_generator = generate_nodes.NodeGenerator()

    def test_elasticsearch_configuration_empty(self):
        es_cache.configure_elasticsearch()
        # es_cache.experimental_test()
        # es_cache.generate_node()

        self.assertTrue(True, True)

    # def test_nodes_with_restfm(self):
    #     bottom_node = self.node_generator.generate_hierarchy()
    #
    #     self.assertEqual(True, True)