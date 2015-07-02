from django import test
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections

from devilry.devilry_elasticsearch_cache import elasticsearch_doctypes
from devilry.devilry_elasticsearch_cache import elasticsearch_registry
from devilry.project.develop.testhelpers import corebuilder

class TestNodeIndexing(test.TestCase):
    def setUp(self):
        connections.get_connection().indices.delete(index='devilry', ignore=404)
        elasticsearch_doctypes.Node.init()
        self.__refresh()

    def __refresh(self):
        elasticsearch_registry.registry.reindex_all()
        connections.get_connection().indices.refresh()

    def test_single_node_indexing(self):
        testnode = corebuilder.NodeBuilder(
            short_name='ducku', long_name='Duckburgh University').node
        self.__refresh()

        indexed_node =  elasticsearch_doctypes.Node.get(id=testnode.id)
        self.assertEqual(indexed_node['short_name'], 'ducku')
        self.assertEqual(indexed_node['long_name'], 'Duckburgh University')

    def test_node_match(self):
        corebuilder.NodeBuilder(
            short_name='ducku',
            long_name='Duckburgh University')
        self.__refresh()

        search = Search()
        search = search.doc_type(elasticsearch_doctypes.Node)
        search = search.query('match', short_name='ducku')

        self.assertEqual(search.to_dict(),
                         {'query': {'match': {'short_name': 'ducku'}}})

        result = search.execute()
        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].long_name, 'Duckburgh University')

    def test_node_match_fuzzy(self):
        corebuilder.NodeBuilder(
            short_name='ducku',
            long_name='Duckburgh University')
        self.__refresh()

        search = Search()
        search = search.doc_type(elasticsearch_doctypes.Node)
        search = search.query('match', long_name='University')

        result = search.execute()
        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].long_name, 'Duckburgh University')

    def test_node_re_indexing(self):
        testnode = corebuilder.NodeBuilder(
            short_name='ducku', long_name='Duckburgh University'
        )
        self.__refresh()

        self.assertEqual(True, True)
