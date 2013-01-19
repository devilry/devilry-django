from django.conf.urls import patterns, url, include

urlpatterns = patterns('devilry_search',
    url('^rest/', include('devilry_search.rest.urls'))
)

