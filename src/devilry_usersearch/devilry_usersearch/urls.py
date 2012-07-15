from django.conf.urls.defaults import patterns, url

from .rest import SearchForUsers

urlpatterns = patterns('devilry_usersearch',
                       url(r'^search', SearchForUsers.as_view()),
                      )

