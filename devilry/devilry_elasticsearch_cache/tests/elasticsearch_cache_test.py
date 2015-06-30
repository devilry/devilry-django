from django import test
from elasticsearch_dsl import Search, Index
from elasticsearch_dsl.connections import connections

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_elasticsearch_cache import elasticsearch_cache as es_cache
from devilry.devilry_elasticsearch_cache import generate_nodes
from devilry.devilry_elasticsearch_cache import elasticsearch_doctypes
from devilry.project.develop.testhelpers import corebuilder


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


class TestNodeIndexing(test.TestCase):
    def setUp(self):
        connections.get_connection().indices.delete(index='devilry', ignore=404)
        elasticsearch_doctypes.Node.init()
        connections.get_connection().indices.refresh()

    def test_single_node_indexing(self):
        corebuilder.NodeBuilder(short_name='ducku',
                                long_name='Duckburgh University')
        connections.get_connection().indices.refresh()

        s = Search()
        s = s.doc_type(NodeDocType)
        s = s.query('match', short_name='docku')
        print s.to_dict()
        result = s.execute()

        for hit in result:
            print hit.title
