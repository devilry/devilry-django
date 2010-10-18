from django.conf.urls.defaults import *

urlpatterns = patterns('devilry.addons.gradestats',
    url(r'^userstats/(?P<period_id>\d+)$',
        'views.userstats',
        name='devilry-gradestats-userstats'),
    url(r'^admin-userstats/(?P<period_id>\d+)/(?P<username>\w+)/$',
        'views.admin_userstats',
        name='devilry-gradestats-admin_userstats'),
    url(r'^admin-periodstats/(?P<period_id>\d+)$',
        'views.admin_periodstats',
        name='devilry-gradestats-admin_periodstats'),
)
