from elasticsearch_dsl import DocType


class Node(DocType):
    # short_name = String()
    # long_name = String()

    class Meta:
        index = 'devilry'

    def save(self, ** kwargs):
        return super(Node, self).save(** kwargs)
