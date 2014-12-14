from django.conf.urls import patterns, url

from .rest import ListHelpLinks

urlpatterns = patterns('devilry.devilry_usersearch',
                       url(r'^helplinks/$', ListHelpLinks.as_view()),
                      )

