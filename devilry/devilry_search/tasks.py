from celery import shared_task
from django.db.models import get_model
from celery.utils.log import get_task_logger

from haystack import connections
from haystack.constants import DEFAULT_ALIAS
from haystack.exceptions import NotHandled


logger = get_task_logger(__name__)


def parse_object_identifier(object_identifier):
    classpath, pk = object_identifier.rsplit('.', 1)
    appname, classname = classpath.rsplit('.', 1)
    model_class = get_model(appname, classname)
    return model_class, pk


def get_searchindex_for_model_class(model_class):
    return connections[DEFAULT_ALIAS].get_unified_index().get_index(model_class)


@shared_task
def haystack_reindex_object(object_identifier):
    model_class, pk = parse_object_identifier(object_identifier)
    try:
        searchindex = get_searchindex_for_model_class(model_class)
    except NotHandled:
        logger.warning(u'The {}-class has no search index configured.'.format(model_class))
    else:
        try:
            instance = model_class.objects.get(pk=pk)
        except model_class.DoesNotExist:
            logger.warning(u'{}: Object not found in the database.'.format(object_identifier))
        else:
            logger.info('Updating search index for %r with pk=%s', model_class, pk)
            searchindex.update_object(instance)


@shared_task
def haystack_delete_object(object_identifier):
    model_class, pk = parse_object_identifier(object_identifier)
    try:
        searchindex = get_searchindex_for_model_class(model_class)
    except NotHandled:
        logger.warning(u'The {}-class has no search index configured.'.format(model_class))
    else:
        try:
            instance = model_class.objects.get(pk=pk)
        except model_class.DoesNotExist:
            logger.warning(u'{}: Object not found in the database.'.format(object_identifier))
        else:
            logger.info('Removing %r with pk=%s from the search index', model_class, pk)
            searchindex.remove_object(instance)
