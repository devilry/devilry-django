from django.conf.urls import patterns, url

from .admincontent import SearchAdminContent
from .studentcontent import SearchStudentContent
from .examinercontent import SearchExaminerContent


urlpatterns = patterns('devilry.devilry_search.rest',
    url(r'^admincontent$', SearchAdminContent.as_view(),
        name='devilry_search_admincontent'),
    url(r'^studentcontent$', SearchStudentContent.as_view(),
        name='devilry_search_studentcontent'),
    url(r'^examinercontent$', SearchExaminerContent.as_view(),
        name='devilry_search_examinercontent')
)
