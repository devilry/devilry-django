from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

import restful

urlpatterns = patterns('devilry.apps.administrator',
                      restful.RestNode.create_rest_url(),
                      url(r'^$', direct_to_template, dict(template='administrator/main.django.html')))
