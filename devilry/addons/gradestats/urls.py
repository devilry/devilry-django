from django.conf.urls.defaults import *

urlpatterns = patterns('devilry.addons.gradestats',
    url(r'^userstats/$',
        'views.userstats',
        name='devilry-gradestats-userstats'),
)
