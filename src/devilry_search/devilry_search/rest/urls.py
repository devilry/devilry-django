from django.conf.urls.defaults import patterns, url

from .admincontent import SearchAdminContent
from .studentcontent import SearchStudentContent


urlpatterns = patterns('devilry_search.rest',
    url(r'^admincontent$', SearchAdminContent.as_view(),
        name='devilry_search_admincontent'),
    url(r'^studentcontent$', SearchStudentContent.as_view(),
        name='devilry_search_studentcontent')
)
