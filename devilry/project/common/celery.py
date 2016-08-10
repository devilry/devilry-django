from __future__ import absolute_import
import os
from celery import Celery


# Ensure this matches your
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devilry.project.settingsproxy')

# The ``main``-argument is used as prefix for celery task names.
app = Celery(main='devilry')

# We put all the celery settings in out Django settings so we use
# this line to load Celery settings from Django settings.
# You could also add configuration for celery directly in this
# file using app.conf.update(...)
app.config_from_object('django.conf:settings')


# This debug task is only here to make it easier to verify that
# celery is working properly.
@app.task(bind=True)
def debug_add_task(self, a, b):
    print('Request: {} - Running {} + {}, and returning the result.'.format(
        self.request, a, b))
    return a + b
