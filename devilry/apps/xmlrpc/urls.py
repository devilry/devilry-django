from django.conf.urls.defaults import *


urlpatterns = patterns('devilry.apps.xmlrpc',
    url(r'^$', 'views.rpc', name='devilry-xmlrpc-login'),
)
