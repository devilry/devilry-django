from celery import shared_task


@shared_task()
def add(x, y):
    print 'Add was called! with x:{}, y:{}'.format(x, y)
    return x + y
