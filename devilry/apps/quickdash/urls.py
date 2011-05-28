from django.conf.urls.defaults import *


urlpatterns = patterns('devilry.apps.quickdash',
    url(r'^$',
        'views.main', name='devilry-main'),
)
