from elasticsearch import Elasticsearch as ES, Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import Mapping
from elasticsearch_dsl import String
from elasticsearch_dsl import Nested
from elasticsearch_dsl import Index
from elasticsearch_dsl import DocType
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import analyzer

import json, requests
from devilry.apps.core.models import Node

ES_URL = 'http://127.0.0.1:9200'

elasticsearch = connections.create_connection(hosts=['localhost:9200'])
devilry_hierarchy = Index('devilry')
devilry_hierarchy.settings(number_of_shards=1, number_of_replicas=0)


class ES_Node(DocType):
    title = String(index='not_analyzed')

    class Meta:
        index = 'devilry'

    def save(self, ** kwargs):
        return super(ES_Node, self).save(** kwargs)


def configure_elasticsearch():

    devilry_hierarchy.doc_type(ES_Node)
    devilry_hierarchy.delete(ignore=404)
    devilry_hierarchy.create()

    ES_Node.init()
    es_node = ES_Node(title='Node Med')
    es_node.save()

    es_node = ES_Node(title='Node Ifi')
    es_node.save()

    es_node = ES_Node(title='Node Matnat')
    es_node.save()

    es_node = ES_Node(title='Node UiO')
    es_node.save()

    # client = Elasticsearch(ES_URL)
    # s = Search(client).index('devilry_hierarchy').doc_type('e_s__node')
    # s = s.query("match", title='Node Med')
    # response = s.execute()

    elasticsearch.indices.refresh()

    s = Search()
    s = s.doc_type(ES_Node)
    s = s.query('match', title='Node Ifi')
    print s.to_dict()
    result = s.execute()

    for hit in result:
        print hit.title

    delete_index(devilry_hierarchy)

def delete_index(index):
    index.delete(ignore=404)