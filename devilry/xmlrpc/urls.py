from django.conf.urls.defaults import *


urlpatterns = patterns('devilry.xmlrpc',
    url(r'^$', 'views.rpc', name='devilry-xmlrpc-login'),
)
