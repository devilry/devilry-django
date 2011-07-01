from django.conf.urls.defaults import patterns
import restful

urlpatterns = patterns('devilry.apps.administrator',
                      restful.RestNode.create_rest_url())
