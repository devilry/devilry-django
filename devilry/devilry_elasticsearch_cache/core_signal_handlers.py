from devilry.devilry_elasticsearch_cache import elasticsearch_doctypes


def index_node_post_save(sender, instance, **kwargs):
    node = instance
    es_node = elasticsearch_doctypes.Node(
        _id=node.id,
        short_name=node.short_name,
        long_name=node.long_name)
    es_node.save()
