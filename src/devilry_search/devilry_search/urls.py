from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required

from .views.search import SearchView
from .views.about_me import AboutMeView

urlpatterns = patterns('devilry_search',
                       url('^rest/', include('devilry_search.rest.urls')),
                       url('^$', login_required(SearchView.as_view()), name='devilry_search'),
                       url('^about_me$',
                           login_required(AboutMeView.as_view()),
                           name='devilry_search_aboutme'))
