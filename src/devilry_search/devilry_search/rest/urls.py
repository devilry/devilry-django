from django.conf.urls.defaults import patterns, url

from .admincontent import SearchAdminContent


urlpatterns = patterns('devilry_search.rest',
    url(r'^admincontent$', SearchAdminContent.as_view()),
)
