from django.conf.urls import patterns, url

from .assignmentlisting import AssignmentListing

urlpatterns = patterns('',
    url(r'^assignmentlisting(\.(?P<_format>[a-zA-Z]+))?/?$',
        AssignmentListing.as_view(),
        name='devilry_examiner-rest-assignmentlisting'),
)
