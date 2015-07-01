# from elasticsearch import Elasticsearch as ES, Elasticsearch
# from elasticsearch_dsl import Search
# from elasticsearch_dsl import Mapping
# from elasticsearch_dsl import String
# from elasticsearch_dsl import Nested
# from elasticsearch_dsl import Index
# from elasticsearch_dsl import DocType
# from elasticsearch_dsl.connections import connections
# from elasticsearch_dsl import analyzer
#
# import json, requests
# from devilry.apps.core.models import Node
#
# ES_URL = 'http://127.0.0.1:9200'
#
# elasticsearch = connections.create_connection(hosts=['localhost:9200'])
# devilry_hierarchy = Index('devilry')
# devilry_hierarchy.settings(number_of_shards=1, number_of_replicas=0)
#
#
# class NodeDocType(DocType):
#     short_name = String()
#     long_name = String(index='not_analyzed')
#
#     class Meta:
#         index = 'devilry'
#
#     def save(self, ** kwargs):
#         return super(NodeDocType, self).save(** kwargs)
#
#
# def configure_elasticsearch():
#
#     devilry_hierarchy.doc_type(NodeDocType)
#     devilry_hierarchy.delete(ignore=404)
#     devilry_hierarchy.create()
#
#     NodeDocType.init()
#     es_node = NodeDocType(long_name='Node Med')
#     es_node.save()
#
#     es_node = NodeDocType(long_name='Node Ifi')
#     es_node.save()
#
#     es_node = NodeDocType(long_name='Node Matnat')
#     es_node.save()
#
#     es_node = NodeDocType(long_name='Node UiO')
#     es_node.save()
#
#     # client = Elasticsearch(ES_URL)
#     # s = Search(client).index('devilry_hierarchy').doc_type('e_s__node')
#     # s = s.query("match", long_name='Node Med')
#     # response = s.execute()
#
#     connections.get_connection().indices.refresh()
#
#     s = Search()
#     s = s.doc_type(NodeDocType)
#     s = s.query('match', long_name='Node Ifi')
#     print s.to_dict()
#     result = s.execute()
#
#     for hit in result:
#         print hit.long_name
#
#     delete_index(devilry_hierarchy)
#
# def delete_index(index):
#     index.delete(ignore=404)
#
#
#
