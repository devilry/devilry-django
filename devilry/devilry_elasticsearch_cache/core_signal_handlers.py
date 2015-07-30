from devilry.devilry_elasticsearch_cache.doctypes import elasticsearch_basenodes_doctypes
from devilry.devilry_elasticsearch_cache.doctypes import elasticsearch_group_doctypes
from tasks import celery_save_es_model


def index_node_post_save(sender, instance, **kwargs):
    node = instance
    es_node = elasticsearch_basenodes_doctypes.Node(
        _id=node.id,
        short_name=node.short_name,
        long_name=node.long_name)
    celery_save_es_model(es_node=es_node)
    # celery_save_es_model.apply_async(countdown=1, es_node=es_node)

def index_subject_post_save(sender, instance, **kwargs):
    subject = instance
    es_subject = elasticsearch_basenodes_doctypes.Subject(
        _id=subject.id,
        short_name=subject.short_name,
        long_name=subject.long_name)
    celery_save_es_model(es_node=es_subject)
    # celery_save_es_model.apply_async(countdown=1, es_node=es_subject)

def index_period_post_save(sender, instance, **kwargs):
    period = instance
    es_period = elasticsearch_basenodes_doctypes.Period(
        _id=period.id,
        short_name=period.short_name,
        long_name=period.long_name)
    celery_save_es_model(es_node=es_period)
    # celery_save_es_model.apply_async(countdown=1, es_node=es_period)

def index_assignment_post_save(sender, instance, **kwargs):
    assignment = instance
    es_assignment = elasticsearch_basenodes_doctypes.Assignment(
        _id=assignment.id,
        short_name=assignment.short_name,
        long_name=assignment.long_name)
    celery_save_es_model(es_node=es_assignment)
    # celery_save_es_model.apply_async(countdown=1, es_node=es_assignment)

def index_assignment_group_post_save(sender, instance, **kwargs):
    assignment_group = instance
    es_assignment_group = elasticsearch_group_doctypes.AssignmentGroup(
        _id=assignment_group.id,
    )
    celery_save_es_model(es_node=es_assignment_group)
    # celery_save_es_model.apply_async(countdown=1, es_node=es_assignment_group)

def index_feedback_set_post_save(sender, instance, **kwargs):
    feedback_set = instance
    es_feedback_set = elasticsearch_group_doctypes.FeedbackSet(
        _id=feedback_set.id,
    )
    celery_save_es_model(es_node=es_feedback_set)
    # celery_save_es_model.apply_async(countdown=1, es_node=es_feedback_set)

def index_group_comment_post_save(sender, instance, **kwargs):
    group_comment = instance
    es_group_comment = elasticsearch_group_doctypes.GroupComment(
        _id=group_comment.id,
    )
    celery_save_es_model(es_node=es_group_comment)
    # celery_save_es_model.apply_async(countdown=1, es_node=es_group_comment)