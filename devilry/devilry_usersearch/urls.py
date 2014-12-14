from django.conf.urls import patterns, url

from devilry.devilry_usersearch.rest import SearchForUsers

urlpatterns = patterns('devilry.devilry_usersearch',
                       url(r'^search$', SearchForUsers.as_view()),
                      )

