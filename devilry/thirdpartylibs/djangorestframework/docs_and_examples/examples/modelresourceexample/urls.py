from django.conf.urls import patterns, url
from devilry.thirdpartylibs.djangorestframework.views import ListOrCreateModelView, InstanceModelView
from modelresourceexample.resources import MyModelResource

urlpatterns = patterns('',
    url(r'^$',          ListOrCreateModelView.as_view(resource=MyModelResource), name='model-resource-root'),
    url(r'^(?P<pk>[0-9]+)/$', InstanceModelView.as_view(resource=MyModelResource)),
)
