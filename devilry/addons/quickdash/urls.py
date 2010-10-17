from django.conf.urls.defaults import *


urlpatterns = patterns('devilry.addons.quickdash',
    url(r'^$',
        'views.main', name='devilry-quickdash-main'),
    url(r'^quickdash-set-focus$',
        'views.set_focus', name='devilry-quickdash-set-focus'),
)
