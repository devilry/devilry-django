from django import test
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections

from devilry.devilry_elasticsearch_cache.doctypes import elasticsearch_basenodes_doctypes, elasticsearch_group_doctypes
from devilry.devilry_elasticsearch_cache import elasticsearch_registry
from devilry.project.develop.testhelpers import corebuilder


class TestNodeIndexing(test.TestCase):
    def setUp(self):
        elasticsearch_basenodes_doctypes.Node.init()
        self.__delete_indexes()
        #self.__reindex_and_refresh()

    def __delete_indexes(self):
        '''
        Delete all indexes.
        '''
        elasticsearch_registry.registry.delete_all()

    def __reindex_and_refresh(self):
        '''
        Reindex to update structure changes in RegistryItem,
        and refresh the indeces to make sure write operations
        are completed before the query/queries execute.
        '''
        elasticsearch_registry.registry.reindex_all()
        connections.get_connection().indices.refresh()

    def test_single_node_indexing(self):
        testnode = corebuilder.NodeBuilder(
            short_name='ducku', long_name='Duckburgh University').node
        self.__reindex_and_refresh()

        indexed_node =  elasticsearch_basenodes_doctypes.Node.get(id=testnode.id)
        self.assertEqual(indexed_node['short_name'], 'ducku')
        self.assertEqual(indexed_node['long_name'], 'Duckburgh University')

    def test_node_match(self):
        corebuilder.NodeBuilder(
            short_name='ducku',
            long_name='Duckburgh University')
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Node)
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
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Node)
        search = search.query('match', long_name='University')

        result = search.execute()
        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].long_name, 'Duckburgh University')

    def test_freesearch_searchtext_single_hit(self):
        self.__reindex_and_refresh()
        node = elasticsearch_basenodes_doctypes.Node()
        node.short_name = 'duck1010'
        node.long_name = 'Duck1010 - Duckoriented programming'
        node.search_text = 'duck1010 DUCK1010 - Duckoriented programming iod IoD ducku Duckburgh University'
        node.save()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Node)
        search = search.query('match', search_text='University')
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].long_name, 'Duck1010 - Duckoriented programming')

    def test_freesearch_searchtext_multiple_hits(self):
        node = elasticsearch_basenodes_doctypes.Node()
        node.short_name = 'duck1010'
        node.long_name = 'Duck1010 - Duckoriented programming'
        node.search_text = 'duck1010 DUCK1010 - Duckoriented programming iod IoD ducku Duckburgh University'
        node.save()

        node = elasticsearch_basenodes_doctypes.Node()
        node.short_name = 'duck1100'
        node.long_name = 'Duck1100 - Programming for Ducklike Sciences'
        node.search_text = 'duck1100 DUCK1100 - Duck1100 - Programming for Ducklike Sciences iod IoD ducku Duckburgh University'
        node.save()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Node)
        search = search.query('match', search_text='IoD')
        result = search.execute()

        self.assertEqual(len(result.hits), 2)

    def test_freesearch_searchtext_multiple_docs_single_hit(self):
        node = elasticsearch_basenodes_doctypes.Node()
        node.short_name = 'duck1010'
        node.long_name = 'Duck1010 - Duckoriented programming'
        node.search_text = 'duck1010 DUCK1010 - Duckoriented programming iod IoD ducku Duckburgh University'
        node.save()

        node = elasticsearch_basenodes_doctypes.Node()
        node.short_name = 'duck1100'
        node.long_name = 'Duck1100 - Programming for Ducklike Sciences'
        node.search_text = 'duck1100 DUCK1100 - Duck1100 - Programming for Ducklike Sciences iod IoD ducku Duckburgh University'
        node.save()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Node)
        search = search.query('match', search_text='Ducklike')
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result.hits[0].short_name, 'duck1100')

    def test_subject_match(self):
        c = corebuilder.SubjectBuilder.quickadd_ducku_duck1010()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Subject)
        search = search.query('match', short_name='duck1010')
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].short_name, 'duck1010')

    def test_period_match(self):
        corebuilder.PeriodBuilder.quickadd_ducku_duck1010_active()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Period)
        search = search.query('match', short_name='active')
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].short_name, 'active')

    def test_assignment_match(self):
        corebuilder.AssignmentBuilder.quickadd_ducku_duck1010_active_assignment1()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Assignment)
        search = search.query('match', short_name='assignment1')
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].short_name, 'assignment1')