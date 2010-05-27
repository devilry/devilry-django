from django.conf.urls.defaults import *


urlpatterns = patterns('devilry.addons.xmlrpc',
    url(r'^$', 'views.rpc'),
)
