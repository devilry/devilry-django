from django.conf.urls.defaults import patterns, url
import restful

urlpatterns = patterns('',
                      restful.RestNode.create_rest_url())
