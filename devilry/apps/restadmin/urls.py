from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required


from restnode import RestNode
from devilry.rest.restview import RestView

urlpatterns = patterns('devilry.apps.restadmin',
                       url(r'^(?P<id>\w+)?(?P<suffix>\.\w+)?$',
                           login_required(RestView.as_view(RestNode)))
                      )
