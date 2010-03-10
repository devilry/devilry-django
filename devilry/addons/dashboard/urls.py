from django.conf.urls.defaults import *


urlpatterns = patterns('devilry.addons.dashboard',
    url(r'^$',
        'views.main', name='main'),
                           
)
