from elasticsearch_dsl import DocType, String


class Node(DocType):
    # short_name = String(index='not_analyzed')
    # long_name = String(index='not_analyzed')

    class Meta:
        index = 'devilry'

    def save(self, ** kwargs):
        return super(Node, self).save(** kwargs)
