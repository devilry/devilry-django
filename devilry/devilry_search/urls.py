from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required

from .views.search import SearchView

urlpatterns = patterns('devilry.devilry_search',
                       url('^rest/', include('devilry.devilry_search.rest.urls')),
                       url('^$', login_required(SearchView.as_view()), name='devilry_search'))
