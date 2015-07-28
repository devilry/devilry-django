from celery import shared_task
from devilry.project.common.celery import app


@app.task(bind=True)
def celery_save_es_model(**kwargs):
    print 'saving es model'
    return kwargs.save()