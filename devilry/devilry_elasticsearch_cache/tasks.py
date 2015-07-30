from celery import shared_task
from devilry.project.common.celery import app


# @app.task(bind=True)
@shared_task()
def celery_save_es_model(**kwargs):
    es_node = kwargs.get("es_node", None)
    doctype_object = kwargs.get("doctype_object", None)
    if doctype_object is not None:
        doctype_object.save()
    if es_node is not None:
        es_node.save()