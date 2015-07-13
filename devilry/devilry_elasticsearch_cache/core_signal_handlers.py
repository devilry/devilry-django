from devilry.devilry_elasticsearch_cache import elasticsearch_doctypes


def index_node_post_save(sender, instance, **kwargs):
    node = instance
    es_node = elasticsearch_doctypes.Node(
        _id=node.id,
        short_name=node.short_name,
        long_name=node.long_name)
    es_node.save()

# def index_subject_post_save(sender, instance, **kwargs):
#     subject = instance
#     es_subject = elasticsearch_doctypes.Subject(
#         _id=subject.id,
#         short_name=subject.short_name,
#         long_name=subject.long_name)
#     es_subject.save()
#
# def index_period_post_save(sender, instance, **kwargs):
#     period = instance
#     es_period = elasticsearch_doctypes.Period(
#         _id=period.id,
#         short_name=period.short_name,
#         long_name=period.long_name)
#     es_period.save()
#
# def index_assignment_post_save(sender, instance, **kwargs):
#     assignment = instance
#     es_assignment = elasticsearch_doctypes.Assignment(
#         _id=assignment.id,
#         short_name=assignment.short_name,
#         long_name=assignment.long_name)
#     es_assignment.save()