from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required

from .views.search import SearchView

urlpatterns = [
    url('^$', login_required(SearchView.as_view()), name='devilry_search')
]
