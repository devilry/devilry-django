from django.conf.urls.defaults import *


urlpatterns = patterns('devilry.apps.xmlrpc_examiner',
    url(r'^$', 'views.rpc', name='devilry-xmlrpc-examiner'),
)
