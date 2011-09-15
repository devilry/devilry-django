from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from views import AdminStats

urlpatterns = patterns('devilry.apps.statistics',
                       url(r'^admin/(?P<periodid>\d+)$', login_required(AdminStats.as_view())),
                      )
