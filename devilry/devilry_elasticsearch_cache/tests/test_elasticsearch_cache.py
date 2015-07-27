from django import test
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from devilry.apps.core import testhelper
from devilry.project.develop.testhelpers.corebuilder import UserBuilder

from devilry.devilry_elasticsearch_cache.doctypes import elasticsearch_basenodes_doctypes, elasticsearch_group_doctypes
from devilry.devilry_elasticsearch_cache import elasticsearch_registry
from devilry.project.develop.testhelpers import corebuilder
from devilry.project.develop.testhelpers.datebuilder import DateTimeBuilder


class TestNodeIndexing(test.TestCase):
    def setUp(self):
        self.testhelper = testhelper.TestHelper()
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

    def test_unicode_string(self):
        testnode = corebuilder.NodeBuilder(
            short_name=u'd\u00F8cku', long_name=u'D\u00F8ckburgh University').node
        self.__reindex_and_refresh()

        indexed_node =  elasticsearch_basenodes_doctypes.Node.get(id=testnode.id)
        self.assertEqual(indexed_node[u'short_name'], u'd\u00F8cku')
        self.assertEqual(indexed_node[u'long_name'], u'D\u00F8ckburgh University')

    def test_single_node_indexing(self):
        testnode = corebuilder.NodeBuilder(
            short_name=u'ducku', long_name=u'Duckburgh University').node
        self.__reindex_and_refresh()

        indexed_node =  elasticsearch_basenodes_doctypes.Node.get(id=testnode.id)
        self.assertEqual(indexed_node[u'short_name'], u'ducku')
        self.assertEqual(indexed_node[u'long_name'], u'Duckburgh University')

    def test_node_match(self):
        corebuilder.NodeBuilder(
            short_name=u'ducku',
            long_name=u'Duckburgh University')
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Node)
        search = search.query(u'match', short_name=u'ducku')

        self.assertEqual(search.to_dict(),
                         {'query': {'match': {u'short_name': u'ducku'}}})

        result = search.execute()
        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].long_name, u'Duckburgh University')

    def test_node_match_fuzzy(self):
        corebuilder.NodeBuilder(
            short_name='uducku',
            long_name=u'Duckburgh University')
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Node)
        search = search.query('match', long_name=u'University')

        result = search.execute()
        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].long_name, u'Duckburgh University')

    def test_freesearch_searchtext_single_hit(self):
        self.__reindex_and_refresh()
        node = elasticsearch_basenodes_doctypes.Node()
        node.short_name = u'duck1010'
        node.long_name = u'Duck1010 - Duckoriented programming'
        node.search_text = u'duck1010 DUCK1010 - Duckoriented programming iod IoD ducku Duckburgh University'
        node.save()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Node)
        search = search.query('match', search_text=u'University')
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].long_name, u'Duck1010 - Duckoriented programming')

    def test_freesearch_searchtext_multiple_hits(self):
        node = elasticsearch_basenodes_doctypes.Node()
        node.short_name = u'duck1010'
        node.long_name = u'Duck1010 - Duckoriented programming'
        node.search_text = u'duck1010 DUCK1010 - Duckoriented programming iod IoD ducku Duckburgh University'
        node.save()

        node = elasticsearch_basenodes_doctypes.Node()
        node.short_name = u'duck1100'
        node.long_name = u'Duck1100 - Programming for Ducklike Sciences'
        node.search_text = u'duck1100 DUCK1100 - Duck1100 - Programming for Ducklike Sciences iod IoD ducku Duckburgh University'
        node.save()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Node)
        search = search.query('match', search_text=u'IoD')
        result = search.execute()

        self.assertEqual(len(result.hits), 2)

    def test_freesearch_searchtext_multiple_docs_single_hit(self):
        node = elasticsearch_basenodes_doctypes.Node()
        node.short_name = u'duck1010'
        node.long_name = u'Duck1010 - Duckoriented programming'
        node.search_text = u'duck1010 DUCK1010 - Duckoriented programming iod IoD ducku Duckburgh University'
        node.save()

        node = elasticsearch_basenodes_doctypes.Node()
        node.short_name = u'duck1100'
        node.long_name = u'Duck1100 - Programming for Ducklike Sciences'
        node.search_text = u'duck1100 DUCK1100 - Duck1100 - Programming for Ducklike Sciences iod IoD ducku Duckburgh University'
        node.save()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Node)
        search = search.query('match', search_text=u'Ducklike')
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result.hits[0].short_name, u'duck1100')

    def test_subject_match(self):
        corebuilder.SubjectBuilder.quickadd_ducku_duck1010()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Subject)
        search = search.query('match', short_name=u'duck1010')
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].short_name, u'duck1010')

    def test_period_match(self):
        corebuilder.PeriodBuilder.quickadd_ducku_duck1010_active()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Period)
        search = search.query('match', short_name=u'active')
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].short_name, u'active')

    def test_assignment_match(self):
        corebuilder.AssignmentBuilder.quickadd_ducku_duck1010_active_assignment1()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_basenodes_doctypes.Assignment)
        search = search.query('match', short_name=u'assignment1')
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].short_name, u'assignment1')

    def test_assignment_group_match(self):
        corebuilder.AssignmentGroupBuilder.quickadd_ducku_duck1010_active_assignment1_group()
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_group_doctypes.AssignmentGroup)
        search = search.query('match', short_name=u'1')
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].short_name, u'1')

    def test_feedback_set_match(self):
        student = UserBuilder(u'testuser', full_name=u'Test User').user
        examiner = UserBuilder(u'donald', full_name=u'Donald Duck').user
        corebuilder.FeedbackSetBuilder.quickadd_ducku_duck1010_active_assignment1_group_feedbackset(studentuser=student, examiner=examiner)
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_group_doctypes.FeedbackSet)
        search = search.query('match', created_by=examiner.id)
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].created_by, examiner.id)

    def test_group_comment_match(self):
        student = UserBuilder(u'testuser', full_name=u'Test User').user
        examiner = UserBuilder(u'donald', full_name=u'Donald Duck').user
        corebuilder.GroupCommentBuilder.quickadd_ducku_duck1010_active_assignment1_group_feedbackset_groupcomment(studentuser=student, examiner=examiner, comment=u'This is a comment')
        self.__reindex_and_refresh()

        search = Search()
        search = search.doc_type(elasticsearch_group_doctypes.GroupComment)
        search = search.query('match', user=student.id)
        result = search.execute()

        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result[0].user, student.id)
        self.assertEqual(result[0].comment_text, u'This is a comment')

    def test_filtered_search_for_feedback_set_points(self):
        # tests a filtered query for points in range 8-42
        student = UserBuilder(u'testuser', full_name=u'Test User').user
        examiner = UserBuilder(u'donald', full_name=u'Donald Duck').user

        assignment_group = corebuilder.AssignmentGroupBuilder.quickadd_ducku_duck1010_active_assignment1_group()
        assignment_group.add_feedback_set(
            points=8,
            published_by=examiner,
            created_by=examiner,
            deadline_datetime=DateTimeBuilder.now().minus(weeks=1))

        assignment_group.add_feedback_set(
            points=5,
            published_by=examiner,
            created_by=examiner,
            deadline_datetime=DateTimeBuilder.now().minus(weeks=2))

        assignment_group.add_feedback_set(
            points=42,
            published_by=examiner,
            created_by=examiner,
            deadline_datetime=DateTimeBuilder.now().minus(weeks=3))

        assignment_group.add_feedback_set(
            points=2,
            published_by=examiner,
            created_by=examiner,
            deadline_datetime=DateTimeBuilder.now().minus(weeks=4))

        self.__reindex_and_refresh()

        search = Search()
        search = search.filter('range', points={'gte': 8})
        result = search.execute()

        expected_points = [8, 42]

        self.assertEqual(len(result.hits), 2)
        for hit in result:
            self.assertIn(hit.points, expected_points)