from django.conf.urls.defaults import *


urlpatterns = patterns('devilry.addons.quickdash',
    url(r'^$',
        'views.main', name='devilry-main'),
)
