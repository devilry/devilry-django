from django.conf.urls.defaults import *


urlpatterns = patterns('devilry.addons.xmlrpc_examiner',
    url(r'^$', 'views.rpc'),
)
