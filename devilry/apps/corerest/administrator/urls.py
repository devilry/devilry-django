from django.conf.urls.defaults import patterns

from devilry.apps.corerest.administrator.restnode import RestNode

urlpatterns = patterns('devilry.apps.corerest.administrator',
                        RestNode.create_url("node", "corerest-admin", "1.0")
                      )
