from django.conf.urls.defaults import *

urlpatterns = patterns('devilry.addons.gradestats',
    url(r'^userstats/(?P<period_id>\d+)$',
        'views.userstats',
        name='devilry-gradestats-userstats'),
    url(r'^admin-userstats/(?P<period_id>\d+)/(?P<username>\w+)/$',
        'views.admin_userstats',
        name='devilry-gradestats-admin_userstats'),

    url(r'^periodstats/(?P<period_id>\d+)$',
        'views.periodstats',
        name='devilry-gradestats-periodstats'),
    url(r'^periodstats-json/(?P<period_id>\d+)$',
        'views.periodstats_json',
        name='devilry-gradestats-periodstats_json'),
)
