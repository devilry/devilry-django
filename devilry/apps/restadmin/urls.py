from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required


from restnode import RestNode
from devilry.rest.restview import RestView

urlpatterns = patterns('devilry.apps.restadmin',
                        RestNode.create_url("restapi", "1.0")
                      )
